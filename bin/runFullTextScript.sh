qsub predictFullText.py "/nlp/data/agshash/output/STUDY\ DESIGN.kn.lm /home1/a/agshash/Spring_2016/Independent_Study/"$1".txt /nlp/data/agshash/output_predictions/"$1"_STUDY_DESIGN.txt"
qsub predictFullText.py "/nlp/data/agshash/output/BACKGROUND.kn.lm /home1/a/agshash/Spring_2016/Independent_Study/"$1".txt /nlp/data/agshash/output_predictions/"$1"_BACKGROUND.txt"
qsub predictFullText.py "/nlp/data/agshash/output/CONCLUSIONS.kn.lm /home1/a/agshash/Spring_2016/Independent_Study/"$1".txt /nlp/data/agshash/output_predictions/"$1"_CONCLUSIONS.txt"
qsub predictFullText.py "/nlp/data/agshash/output/METHODS.kn.lm /home1/a/agshash/Spring_2016/Independent_Study/"$1".txt /nlp/data/agshash/output_predictions/"$1"_METHODS.txt"
qsub predictFullText.py "/nlp/data/agshash/output/OBJECTIVE.kn.lm /home1/a/agshash/Spring_2016/Independent_Study/"$1".txt /nlp/data/agshash/output_predictions/"$1"_OBJECTIVE.txt"
qsub predictFullText.py "/nlp/data/agshash/output/OTHERS.kn.lm /home1/a/agshash/Spring_2016/Independent_Study/"$1".txt /nlp/data/agshash/output_predictions/"$1"_OTHERS.txt"
qsub predictFullText.py "/nlp/data/agshash/output/RESULTS.kn.lm /home1/a/agshash/Spring_2016/Independent_Study/"$1".txt /nlp/data/agshash/output_predictions/"$1"_RESULTS.txt"