# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 19:04:32 2020
@author: hurtd

WRAPPING PACKAGE to Combine "Hanlding" and "Transformations" to produce
Data To Plot on Demand and deliver to the Image Processing f(n)s


 This package will contain several 'sections':

  * __Perform Transformation__: Wrapper function(s) to actually /do/ the
          transformations. This MAY be smart-ish and perform only specified
          ones, perhaps from a CONFIG or LIST? (That List and Config
          is an idea we'll talk about in __yNot__ probably!)

  * __Association Functions:__ This is optional, but once you've done
          the transformations (or before?) you can check how well the data
          CORRELATES/ASSOCIATES, both to itself and to a "Standard" dataset
          AKA starting with linear data and transforming it!
          This may give us "SCORES" for each transformation,
          which we can use to prioritize!




 __Timeline + Milestones__:
  * 2020-04-21: List of the high-priority functions and
                  Simple-Transformations, with progress and
                  timeline to get them all done soon.
  * 2020-04-28: Passing Tests and can __HAND OFF__ to the classifier - a
                  DataFrame of "all" the transformed data columns.
                  Recieve Handoff from handling, and begin to Integrate.
  * 2020-05-12: Complex Transforms - consider what other things we may want,
                  and discuss feedback with group
  * 2020-06-09: Make Decision on Association functions and __HAND OFF__
                  if so. Otherwise, simply focus on new group priorities
  * 2020-06-23: IF yNot function is doing Configuration ideas, make
                  Stretch-Goal learning gameplan... TBD...

 __Current Status__:
  * (2020-04-14)
  * Just creating files and setup, no progress yet
  * Planning Functions, in compontent spec document (here!)
  * Considering how much to Frankenstien from prior work. Configuration?


 __Module List__:

### *SECTION: Perform Transformation*
#### get_xy():
  * Uses handling.py to load a file, check that we have xy data,
          and do a quick analysis on it!
  * INPUT: file name
  * OUTPUT: each of 1D arrays X and Y, plus messages OR list of
          "Approved" transformations??

#### perform_transform():
  * Wrapping function, to take some input data and return a
          dataframe with every transform that we want to use:
  * INPUT: 1D arrays X, Y, some sort of list or guiance for what
          transforms to do
  * OUTPUT: Pandas dataframe of X and Y with all of their transforms
          as requested.
  * NOTE: There might be a better way to do this -

#### generate_linear_transforms():
  * Creates a "sample" linear 2D dataset, possibly following
          range instructions, and performs all(?) transforms on the data
  * INPUT: [ALL OPTIONAL? Default 0-1 and X=Y], [List of transforms to do??
          default True to perform "ALL"]
  * OUTPUT: pandas dataframe with all X-transformationa and all
          Y-transformations - (Maybe in Standard names? Maybe Not?)
  * NOTE: This could get messy - And maybe use the same wrapping function
          above to perform the listed tranforms?

### *SECTION: Association Functions*
  * NOTE: Not really planning these yet, that will be scoped or
          descoped based on Team Update by __2020-04-28__

#### setup_correlation_matrix():
  * Sets up the 2D matrix of "scores" to judge the correlations

#### correlate_to_transforms():
  * For a given transform, determine (?) how correlated the
          data is to all other columns in the dataframe

#### correlate_to_linear():
  * Compares the given transform to the linear_transform()
          function transforms. Any that correlate are probably good ideas?!?

#### correlate_to_null():
  * Maybe compares the given transform to a flat line of low but
          nonzero values (all value = 0.1)?
  * Not sure what's the best way to do this...
  * What I'm TRYING to do is to identify/flag "BORING" data, which are
          probably BAD transforms to use?

 #### grade_all_transforms():
  * Wrapping function. Given a "fully" transformed dataset
          (or generate it here?), run all correlations and use some
          fancy math or grading (we generate?) to give each column a "SCORE"
  * The __SCORE__ should reflect how "Interesting" we think the data
          is (which is a topic for discussion, but all zeros is
          not interesting)
  * INPUT: dataframe ready to be "graded", OR give an XY dataset and
          we'll call the transform functions on it
  * OUTPUT: dictionary of Key,Values where each Key is a transform
          (or column key), and each Value is a "grade" to estimate
          how interesting we think the data may be
  * NOTE: This is SUPER arbitrary and is the 'creative' part of the
          STRETCH-GOALS of the project.s!

 #### grade_all_files():
  * Load all the files in a list, perform transformations, and grade.
          Hopefully this is a fast function so you can do a large
          list of files.
  * Then combine all the grades to get an average idea of what
          transforms we consider "good"
  * INPUT: list of files
  * OUTPUT: dictionary of key, values as before, where results
          are averaged across dataset
  * ACTIONS: Optionally, save results as a report csv (or append to
          existing csv report??), to track grades over time

 #### load_transform_results():
  * IF we've run this program before, we should have a file that has
          previous "grades", this time based on the model training
  * If one transform shows up in a lot of the best-performing models,
          we should bump it to the top of the Transform To-Do List!

 #### combine_grades_results():
  * Somehow we should combine the 'grades' with the 'prior results'
          to get our new guess for what are the 'best' transformations to try
  * this will allow our model to do the highest-profile transfomations
          first and hopefully get good results in fewer attempts.

"""
