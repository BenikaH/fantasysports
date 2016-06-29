from sklearn import svm
from sklearn.cross_validation import StratifiedKFold
from sklearn.metrics import classification_report
import numpy as np
import random
import conf
import util.util as u
import pandas as pd
from sklearn.externals import joblib
import MySQLdb
import pdb

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="kmeurer",         # your username
                     passwd="kvnmrr-1",  # your password
                     db="retrosheet")        # name of the data base

cur = db.cursor()

# Use all the SQL you like
cur.execute(
    "SELECT DISTINCT game_id, pit_id from starting_pitcher_hist;")

positive_training_entries = []
negative_training_entries = []
# print all the first cell of all the rows
ids_and_pits = random.sample(cur.fetchall(), conf.pitcher_total_samples)
for idx, row in enumerate(ids_and_pits):
    print "Processing pitcher %d of %d" % (idx + 1, len(ids_and_pits))
    cur.execute("CREATE TEMPORARY TABLE pit_res SELECT * FROM starting_pitcher_hist WHERE game_id = '%s' AND pit_id = '%s';" % (row[0], row[1]))
    """LOAD DIFFERENTIAL VALUES"""
    # for IP, ER, and run differential
    cur.execute(
        "SELECT inn_ct - 1 + (outs_ct * (1/3)) as IP, CASE WHEN pit_team = 1 THEN away_score_ct ELSE home_score_ct END as ER, CASE WHEN pit_team = 1 THEN home_score_ct - away_score_ct ELSE away_score_ct - home_score_ct END as RD FROM pit_res;"
    )
    diffs = cur.fetchall()
    """POSITIVE ENTRIES (pitcher taken out)"""
    # they were taken out in the last entry
    pos_diff = [float(s) for s in diffs[len(diffs) - 1]]
    cur.execute("SELECT SUM(event_cd=3) as K, SUM(event_cd=14) as BB, SUM(event_cd=16) as HBP, COUNT(*) as PA, SUM(event_cd=20) + SUM(event_cd=21) + SUM(event_cd=22) + SUM(event_cd=23) as H FROM pit_res;")
    pos_stats = cur.fetchall()[0]
    pos_stats = [float(stat) for stat in pos_stats]
    pos_stats += pos_diff

    """NEGATIVE ENTRIES (pitcher stayed in)"""
    # convert neg diffs to be all floats
    neg_diffs = [[float(a) for a in arr] for arr in diffs[1:]]
    neg_count = len(diffs) - 1
    neg_stats = []
    for i in xrange(neg_count):
        cur.execute("SELECT SUM(A.event_cd=3) as K, SUM(A.event_cd=14) as BB, SUM(A.event_cd=16) as HBP, COUNT(*) as PA, SUM(A.event_cd=20) + SUM(A.event_cd=21) + SUM(A.event_cd=22) + SUM(A.event_cd=23) as H FROM (SELECT * FROM pit_res limit %d) as A;" % (i + 1))
        neg_stat = cur.fetchall()[0]
        neg_stats.append([float(stat) for stat in neg_stat])
    """LOAD PRIOR GAMES"""
    # for K, BB, PA, and H
    # get count of all items in the list
    neg_stats = map(list.__add__, neg_stats, neg_diffs)
    if len(neg_stats) >= conf.pitcher_neg_samples:
        neg_stats = random.sample(neg_stats, conf.pitcher_neg_samples)
    positive_training_entries.append(pos_stats)
    negative_training_entries += neg_stats
    cur.execute('DROP TABLE pit_res')
X = np.array(positive_training_entries + negative_training_entries)
y = np.array(([1] * len(positive_training_entries)) + ([0] * len(negative_training_entries)))
skf = StratifiedKFold(y, n_folds=5)
weights = np.array(([1] * len(positive_training_entries)) + ([1] * len(negative_training_entries)))
for train_index, test_index in skf:
    clf = svm.SVC()
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_true = y[train_index], y[test_index]
    w_train, w_test = weights[train_index], weights[test_index]
    clf.fit(X_train, y_train, sample_weight=w_train)
    y_pred = clf.predict(X_test)
    print classification_report(y_true, y_pred, labels=['0', '1'])

clf = svm.SVC(kernel="linear")
clf.fit(X, y, sample_weight=weights)
joblib.dump(clf, './models/pitcher_sub_model_%d.pkl' % conf.model_iteration)
