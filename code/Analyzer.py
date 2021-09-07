import lizard
import pandas as pd


class Analyzer:

    def __init__(self, df, hub):
        self.df = df
        self.hub = hub
        self.duplicates = 0
        self.owner_comments = 0
        self.nan_data = 0
        self.left_side_cases = 0
        self.no_valid_ref = 0
        self.no_comment = 0
        self.comm_to_comm = 0
        self.no_method_before = 0
        self.before_equal_after = 0
        self.no_marked = 0
        self.no_method_after = 0

    def remove_duplicates(self):
        self.duplicates = len(self.df) - len(self.df.drop_duplicates())
        self.df = self.df.drop_duplicates()

    def remove_owner_comments(self):
        new_df = self.df[self.df['change_owner'] != 'owner'] if (self.hub == 'Gerrit') \
            else self.df[self.df['user_id'] != self.df['owner_id']]
        self.owner_comments = len(self.df) - len(new_df)
        self.df = new_df

    def remove_left_side(self):
        if self.hub == 'GitHub':
            self.left_side_cases = len(self.df) - len(self.df[self.df['side'] != 'LEFT'])
            self.df = self.df[self.df['side'] != 'LEFT']

    def remove_nan_data(self):
        new_df = self.df.dropna(subset=['message', 'file_content_before', 'file_content_after']) if (
                    self.hub == 'Gerrit') else self.df.dropna(
            subset=['message', 'file_content_while', 'file_content_after'])
        self.nan_data = len(self.df) - len(new_df)
        self.df = new_df

    def analyze_data(self):
        df = self.df

        comments = []
        before_methods = []
        before_marked_methods = []
        after_methods = []
        # df_index = []
        pull_ids = []
        pull_nums = []
        filenames = []
        method_names = []

        for idx, row in df.iterrows():

            # check ref to line
            if self.hub == 'Gerrit':
                if row.line == 0 & row.comment_start_line == 0:
                    self.no_valid_ref += 1
                    continue

            # check comment
            comm = row.message.strip()
            if len(comm) == 0:
                self.no_comment += 1
                continue

            # save info
            id_ref, num_ref, ref, filename = Analyzer.get_info(row, self.hub)

            # save code before and code after in a temp file
            Analyzer.save_temp_code(row, self.hub)

            # check refs are in code
            if not Analyzer.check_len_code(ref[0], ref[1]):
                self.no_valid_ref += 1
                continue

            # check comment to comment
            if Analyzer.check_comment_to_comment(ref[0], ref[1]):
                self.comm_to_comm += 1
                continue

            # searching for before method
            before_found = Analyzer.search_before_method(ref)
            if len(before_found) != 1:
                self.no_method_before += 1
                continue

            # save before method
            before = Analyzer.extract_method(before_found[0], 'before')
            if len(before) == 0:
                self.no_method_before += 1
                continue

            # mark method before with <START>, <END> tokens
            before_marked, flag_marked = Analyzer.extract_marked_method(before_found[0], ref, self.hub)
            if not flag_marked:
                self.no_marked += 1
                continue

            # searching for after method
            signature = before_found[0].long_name
            after_found = Analyzer.search_after_method(signature)
            if len(after_found) == 0:
                self.no_method_after += 1
                continue

            # save after method
            after = Analyzer.extract_method(after_found[0], 'after')
            if len(after) == 0:
                self.no_method_after += 1
                continue

            # check before method != after method
            if before == after:
                self.before_equal_after += 1
                continue

            # save data extracted
            comments.append(comm)

            new_before = ''
            for line in before:
                new_before += line
            before_methods.append(new_before)

            new_before_marked = ''
            for line in before_marked:
                new_before_marked += line + '\n'
            before_marked_methods.append(new_before_marked)

            new_after = ''
            for line in after:
                new_after += line
            after_methods.append(new_after)

            # df_index.append(idx)
            pull_nums.append(num_ref)
            pull_ids.append(id_ref)
            filenames.append(filename)
            method_names.append(signature)

        dfr = pd.DataFrame({
            # 'id_df': df_index,
            'pull_num': pull_nums,
            'pull_id': pull_ids,
            'filename': filenames,
            'method_name': method_names,
            'comment': comments,
            'before': before_methods,
            'before_marked': before_marked_methods,
            'after': after_methods
        })

        # dfr = dfr.drop(["id_df"], axis=1)

        return dfr

    @staticmethod
    def get_info(row, hub):
        id_ref, num_ref, ref = Analyzer.get_info_gerrit(row) if hub == 'Gerrit' else Analyzer.get_info_github(row)
        filename = row.filename
        return id_ref, num_ref, ref, filename

    @staticmethod
    def get_info_github(row):
        pull_id = row.pull_id
        pull_num = row.pull_number

        if str(row.original_start_line) != 'nan':
            ref = [int(row.original_start_line), row.original_line]
        else:
            ref = [row.original_line, row.original_line]

        return pull_id, pull_num, ref

    @staticmethod
    def get_info_gerrit(row):
        change_id = row.change_id
        rev_num = row.revision_number

        ref = []
        start_line = row.comment_start_line
        line = row.line
        end_line = row.comment_end_line
        start_char = row.start_character
        end_char = row.end_character

        if start_line != 0:
            ref.append(start_line)
        else:
            ref.append(line)
        if end_line != 0:
            ref.append(end_line)
        else:
            ref.append(ref[0])

        if start_char != 0 and end_char != 0:
            ref.append(start_char)
            ref.append(end_char)

        return change_id, rev_num, ref

    @staticmethod
    def save_temp_code(row, hub):
        f = open('before.java', 'w')
        if hub == 'GitHub':
            f.write(row.file_content_while)
        else:
            f.write(row.file_content_before)
        f.close()

        f = open('after.java', 'w')
        f.write(row.file_content_after)
        f.close()

    @staticmethod
    def check_len_code(start_line, end_line):
        code_lines = [line for line in open('before.java')]
        if start_line > len(code_lines) or end_line > len(code_lines):
            return False
        return True

    @staticmethod
    def check_comment_to_comment(start_line, end_line):
        code_lines = [line.strip() for line in open('before.java')]
        k = start_line
        while k <= end_line:
            current_line = code_lines[k - 1]
            if len(current_line) == 0:
                k += 1
                continue
            if not current_line.startswith('/') and not current_line.startswith('*'):
                return False
            k += 1
            return True
        return False

    @staticmethod
    def search_before_method(ref):
        method_found = []
        liz = lizard.analyze_file('before.java')
        for liz_elem in liz.function_list:
            if (liz_elem.start_line <= ref[0]) and (liz_elem.end_line >= ref[1]):
                method_found.append(liz_elem)
        return method_found

    @staticmethod
    def search_after_method(elem_name):
        method_found = []
        liz = lizard.analyze_file('after.java')
        for liz_elem in liz.function_list:
            if liz_elem.long_name == elem_name:
                method_found.append(liz_elem)
                break
        return method_found

    @staticmethod
    def extract_method(liz_elem, before_or_after):
        method_extracted = []

        if before_or_after == 'after':
            code = [line for line in open('after.java')]
        else:
            code = [line for line in open('before.java')]

        for k in range(len(code)):
            method_extracted = code[liz_elem.start_line - 1: liz_elem.end_line]
        if len(method_extracted) != 0:
            if len(method_extracted[-1].strip()) != 0:
                # chek other lines if the last one is empty ?
                if not method_extracted[-1].strip().endswith('}'):
                    return []
        return method_extracted

    @staticmethod
    def extract_marked_method(liz_elem, ref, hub):
        if hub == 'Gerrit' and len(ref) == 4:
            m, f = Analyzer.extract_marked_method_gerrit(liz_elem, ref)
        else:
            m, f = Analyzer.extract_marked_method_github(liz_elem, ref)
        return m, f

    @staticmethod
    def extract_marked_method_github(liz_elem, ref):
        flag_marked = False
        code = [line for line in open('before.java')]
        method_extracted_marked = []
        for k in range(len(code)):
            if liz_elem.start_line - 1 <= k <= liz_elem.end_line - 1:
                if code[k].endswith('\n'):
                    current_line = code[k][:-1]
                else:
                    current_line = code[k]
                if k + 1 == ref[0]:
                    if ref[0] == ref[1]:
                        current_line = '<START> ' + current_line + ' <END> '
                        flag_marked = True
                    else:
                        current_line = '<START> ' + current_line
                if k + 1 == ref[1] and not flag_marked:
                    current_line += ' <END> '
                    flag_marked = True
                method_extracted_marked.append(current_line)
        return method_extracted_marked, flag_marked

    @staticmethod
    def extract_marked_method_gerrit(liz_elem, ref):
        flag_marked = False
        flag_char = False
        if ref[2] != 0 or ref[3] != 0:
            flag_char = True
        file = open('before.java', 'r')
        code = [line for line in file]
        file.close()
        method_extracted_marked = []
        for k in range(len(code)):
            if liz_elem.start_line - 1 <= k <= liz_elem.end_line - 1:
                if code[k].endswith('\n'):
                    current_line = code[k][:-1]
                else:
                    current_line = code[k]
                if k + 1 == ref[0]:  # comment_start_line
                    if not flag_char:
                        current_line = '<START> ' + current_line
                    else:
                        if ref[0] == ref[1]:
                            new_current_line = Analyzer.add_end(current_line, ref[3])
                            if new_current_line == current_line:
                                break
                            else:
                                current_line = new_current_line
                            new_current_line = Analyzer.add_start(current_line, ref[2])
                            if new_current_line == current_line:
                                break
                            else:
                                current_line = new_current_line
                                flag_marked = True
                        else:
                            new_current_line = Analyzer.add_start(current_line, ref[2])
                            if new_current_line == current_line:
                                break
                            else:
                                current_line = new_current_line
                if k + 1 == ref[1] and not flag_marked:
                    if not flag_char:
                        current_line = current_line + ' <END> '
                        flag_marked = True
                    else:
                        new_current_line = Analyzer.add_end(current_line, ref[3])
                        if new_current_line == current_line:
                            break
                        else:
                            current_line = new_current_line
                            flag_marked = True
                method_extracted_marked.append(current_line)
        return method_extracted_marked, flag_marked

    @staticmethod
    def add_start(text, start_char):
        try:
            if text[start_char - 1] == ' ':
                new_text = text[:start_char - 1] + ' <START> ' + text[start_char - 1:]
            else:
                flag = False
                k = 2
                while not flag and start_char - k > 0:
                    if text[start_char - k] == ' ':
                        flag = True
                    else:
                        k += 1
                if flag:
                    new_text = text[:start_char - k] + ' <START>' + text[start_char - k:]
                else:
                    new_text = '<START> ' + text
        except:
            # print('WARNING ADD START')
            new_text = '<START> ' + text
        return new_text

    @staticmethod
    def add_end(text, end_char):
        try:
            if text[end_char - 1] == ' ':
                new_text = text[:end_char - 1] + ' <END> ' + text[end_char - 1:]
            else:
                flag = False
                k = 2
                while not flag and end_char + k < len(text):
                    if text[end_char + k] == ' ':
                        flag = True
                    else:
                        k += 1
                if flag:
                    new_text = text[:end_char + k] + ' <END> ' + text[end_char + k:]
                else:
                    new_text = text + ' <END> '
        except:
            # print('WARNING ADD END')
            new_text = text + ' <END> '
        return new_text
