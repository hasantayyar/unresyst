Welcome to the Unresyst CD!
---------------------------

Current versions of all contained files can be found on http://code.google.com/p/unresyst/

The directory structure of the CD is the following:

 - docs: documentation of the unresyst prototype implementation.
   - diagrams: various diagrams used in the thesis, created in dia, a program for drawing structured diagrams http://live.gnome.org/Dia
   - evaluation: spreadsheets containing the results of unresyst evaluation, including charts
   - thesis: the thesis in the linked pdf format and latex source codes
   - mindmaps: mind maps used for presenting ideas about Unresyst. Created in XMind version: 3.2.0  http://www.xmind.net/
   - pics: pictures used in the thesis
   - presentations: presentations on the thesis from the User-Web seminar.
   - datamodels: data model visualization for each dataset application and for the whole unresyst.
  
 
   
  - code: contains all source code files belonging to the thesis.

    - adapter: adapter is a django project home directory (see http://www.djangoproject.com/), there are the following applications in the project. Each application has its own directory. The documentation for the project can be found in the docs/epydoc folder.

      - unresyst: the universal recommender application containing the implementation of the universal recommedner
      - lastfm: an application containing data models and a Unresyst recommender for the last.fm dataset.
      - flixster: application for the flixster dataset, the same structure as lastfm
      - travel: application for the travel agency dataset, the same structure as lastfm
      - demo: a demo application used in the tests
      - csv: a directory for temporary csv files used for the external mahout recommender
      - logs: a directory of text files where the evaluation of the recommendations is logged
      - evaluate.txt: a list of commands for running an external recommender for each application
      - example.py: an example of an Unresyst recommender, presented on the User-Web seminar
      - flixstereval.sh, lastfmeval.sh, traveleval.sh: scripts for running an evaluation on example datasets, see the script code for help
      - dump.sh, load.sh: scripts for opperating with the MySQL database
      - setup.sh: a script for loading data from dataset to the corresponing application models, the script just uses python scripts save_data.py, defined in each of the applications.             
      - unresyst/tests/: tests for the implementation, the tests can be run using the command 'python ./manage.py test unresyst"

    - dataset_scripts: shell scripts for reducing the datasets as described in the thesis.

    - mahout: contains an implementation of the Slope One recommender that was used for a comparison with unresyst. The recommender is implemented in Java using the Mahout recommender framework. See http://mahout.apache.org/ and http://code.google.com/p/unresyst/wiki/CreateMahoutRecommender for download and instalation of the Mahout framework.
    
      - unresystrecommend.sh, unresystpredict.sh: the scripts used for running the recommender on our data sets.


