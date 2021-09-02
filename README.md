# code_review_automation

This repository is the replication package of the research work **"Automating Code Review Activities 2.0"**.

In our work we trained different T5 models for different tasks on different datasets. Here we provide everything needed to replicate our experiments. We also provide all our results.

In order to replicate our results you have two options:
* use our fine-tuned models to generate new predictions;
* train from scratch your own models.

For the second option (train your own models) you will need a **Google Colab** pro account and a **Google Cloud Storage** account (more details later).

## Resources

* In the `code` folder we provided the Google Colab notebook we used to:
  * `Preprocessing.ipynb`: preprocess the pre-training dataset and train the Sentencepiece model;
  * `PreTraining.ipynb`: pre-trian the T5 model;
  * `FineTuning.ipynb`: fine-tuning the T5 models on different tasks.

* `manual analysis.xlsx`: contains the results of the manual analysis we performed on some non perfect predictions.

[Here](https://zenodo.org/record/5387856#.YTDrPZ4zZyo) we stored the extra materials you need in order to replicare our results:

* `automating_code_review.zip` contains all the necessary to successfully run our Google Colab notebooks (see section **Train your T5 models** for more details).

* `datasets.zip` contains all the processed and splitted datasets we used:
  * fine-tuning
  * pre-training 
    * `pre-training.tsv`
  * fine-tuning
    * new_large
      * code-to-code
        * `test.tsv`, `train.tsv`, `val.tsv`
      * code-to-comment
        * `test.tsv`, `train.tsv`, `val.tsv`
      * code&comment-to-code
        * `test.tsv`, `train.tsv`, `val.tsv`
    * Tufano_etal_ICSE21
      * code-to-code
        * `test.tsv`, `train.tsv`, `val.tsv`
      * code&comment-to-code
        * `test.tsv`, `train.tsv`, `val.tsv`

* `generate_predictions.zip` contains the material to successfully generate predictions using a T5 model chekpoint (see section **Use our fine-tuned T5 models** for more details)

* `models.zip` contains the (best) checkpoints of our T5 models (pre-trained or not), for all the tasks (_code-to-code_, _code-to-comment_, _code&comment-to-code_) and both the datasets (_new_large_dataset_, _Tufano_etal_dataset_) we used. We also stored the checkpoint of the pre-trained model without any fine-tuning. The following is the content of the `models` folder:
  * T5_non_pre-trained_new_large_dataset_code-to-code
  * T5_non_pre-trained_new_large_dataset_code-to-comment
  * T5_non_pre-trained_new_large_dataset_code&\comment-to-code
  * T5_non_pre-trained_Tufano_etal_dataset_code-to-code
  * T5_non_pre-trained_Tufano_etal_dataset_code&\comment-to-code
  * T5_pre-trained
  * T5_pre-trained_new_large_dataset_code-to-code
  * T5_pre-trained_new_large_dataset_code-to-comment
  * T5_pre-trained_new_large_dataset_code&\comment-to-code
  * T5_pre-trained_Tufano_etal_dataset_code-to-code
  * T5_pre-trained_Tufano_etal_dataset_code&\comment-to-code

* `tokenizer.zip` contains the Sentencepiece model and vocabulary we trained on our pre-training dataset:
  * `TokenizerModel.model`, `TokenizerModel.vocab`

* `results.zip` contains for each dataset (_new_large_dataset_, _Tufano_etal_dataset_) the results obtained from each model (pre-trained or not) fine-tuned on each task (_code-to-code_, _code-to-comment_, _code&comment-to-code_). For each of these cases we stored the following files:
  * `source.txt`: input file for the model;
  * `target.txt`: target file (expected output);
  * `predictions_<k>.txt`: generated predictions file with *BEAM_SIZE = k (k=1,3,5,10)*.
  * `code_bleu_<k>.txt` or `bleu_<k>.txt`: **code_BLEU** or **BLEU** scores file (depending on the task) with *BEAM_SIZE = k (k=1,3,5,10)*
  * `confidence_<k>.txt`: confidence scores file with *BEAM_SIZE = k (k=1,3,5,10)* 


## Train your T5 models

## Use our fine-tuned T5 models

