import os
from subprocess import call
from subprocess import check_output
import uuid
import math

ngram_cmd = "/home1/c/cis530/srilm/ngram-count"
ngram_cmd2 = "/home1/c/cis530/srilm/ngram"
min_count_bi = "20"
min_count_tri = "20"
def srilm_bigram_models(input_file, output_dir):
    basename = os.path.basename(input_file)
    basename = os.path.splitext(basename)[0]
    # out1 = os.path.join(output_dir, "{}.uni.lm".format(basename))
    # out2 = os.path.join(output_dir, "{}.uni.counts".format(basename))
    # call([ngram_cmd, "-text", input_file, "-order", "1", "-addsmooth", "0.25", \
    # "-lm", out1, "-write", out2])

    # out = os.path.join(output_dir, "{}.bi.lm".format(basename))
    # call([ngram_cmd, "-text", input_file, "-order", "2", "-addsmooth", "0.25", \
    # "-lm", out])

    out = os.path.join(output_dir, "{}.kn.lm".format(basename))
    call([ngram_cmd, "-text", input_file, "-order", "3", "-kndiscount", \
            "-gt1min", min_count_bi, "-gt2min", min_count_bi, "-gt3min", \
            min_count_tri, "-lm", out])

def srilm_ppl(model_file, raw_text):
    # print "-------------------------------------------------------"
    # print "In SRILM"
    # tmp = "/home1/a/agshash/Spring_2016/Independent_Study/nate/tmp"
    tmp = "/nlp/data/agshash/tmp/pico"
    textfile = os.path.join(tmp, "ppl_calc_{}".format(uuid.uuid4()))
    with open(textfile, 'w') as f:
        f.write(raw_text)
    # print "Temp file written"
    out = check_output([ngram_cmd2, "-lm", model_file, "-ppl", textfile])
    # print "Prediction Completed"
    split = out.split(" ")
    ppl = split[split.index("ppl=") + 1]
    # print "PPL set"
    os.remove(textfile)
    # print "Temp file removed"
    # print "-------------------------------------------------------"
    return float(ppl)

def srilm_prob(model_file, raw_text):
    tmp = "/home1/a/agshash/Spring_2016/Independent_Study/nate/tmp"
    textfile = os.path.join(tmp, "ppl_calc_{}".format(uuid.uuid4()))
    with open(textfile, 'w') as f:
        f.write(raw_text)
    out = check_output([ngram_cmd2, "-lm", model_file, "-ppl", textfile])
    split = out.split(" ")
    logprob = float(split[split.index("logprob=") + 1])
    prob = math.pow(10, logprob)
    
    os.remove(textfile)

    return prob
