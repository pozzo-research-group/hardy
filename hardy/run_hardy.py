# from datetime import datetime
import time
import os.path
import yaml

import hardy.recognition.cnn as cnn
import hardy.recognition.tuner as tuner
import hardy.data_reporting.reporting as reporting

from hardy.handling import pre_processing as preprocessing
from hardy.handling import to_catalogue as to_catalogue
from hardy.arbitrage import arbitrage


def hardy_multi_transform(  # Data and Config Paths
                          raw_datapath, tform_config_path,
                          classifier_config_path,
                          # Optional for Data
                          iterator_mode='arrays', plot_format="RGBrgb",
                          print_out=True, skiprows=0,
                          # Optional for Classifier
                          num_test_files_class=300, scale=1.0,
                          classifier='tuner', split=0.1, target_size=(80, 80),
                          batch_size=32, classes=['class_1', 'class_2'],
                          project_name='tuner_run', k_fold=False, k=None,
                          color_mode='rgb'):
    """
    OVERALL wrapper function, to pass initial configurations and allow
        all other internal functions to understand and call upon each other.

    Parameters:
    -------------
    raw_datapath : str
                   path to the raw .csv files containing the data to classify
    tform_config_path : str
                        string containing the path to the yaml file
                        containing the transformations to use and which
                        data in the .csv file to perform it on
    classifier_config_path : str
                             string containing the path to the yaml file
                             representing the classifier hyperparameters
    iterator_mode : str
                    option to use images from arrays directly or save the
                    .png and use a directory iterator mode
    plot_format : str
                  option for standard or RGB color gradient
    print_out : bool
                option for printing out feedback on conputational time taken to
                initialize the data and generate the images
    num_test_files_class : int or float
                            numebr of files per class to select for the test
                            set
    classifier : str
                  option cnn or tuner
    scale :  float
             percentage fo the image to reduce its size to.
    split : float
            the percentage of the learning set to use for the validation step
    target_size : tuple
                  image target size. Presented as a tuble indicating number of
                  pixels composing the two dimensions of the image (w x h)
    batch_size : int
                 The number of files to group up into a batch

    classes : list
              A list containing strings of the classes the data is divided in.
              The class name represent the folder name the files are contained
              in.
    project_name : str
                   name of the folder to be created for storing the results of
                   the tuning

    Function Calls:  (see their related documentation)
    ---------------
        import_tform_config :   f(n) of ARBITRAGE.py
                                Import the list and dictionary of transforms
                                to be looped through.
                                (full model and report for each)

        data_wrapper :  Local Wrapping f(n)
                        Takes file path and the transformation command
                        for the current loop, and creates the list-of-tuple
                        images (OR Saves Image Files to be used later)

        classifier_wrapper :    Local Wrapping f(n)
                                Takes many inputs including configuration
                                loading directions. Loads images, and
                                makes them Keras-Readable.
                                Then sets up the model and the tuner,
                                and runs the model test/train/tune loops
                                as commanded.

    Returns
    -------
    * returns a folder containing subfolders, one for each trial run in the
    hardy module. THese folders will containg a report on the run, as well as
    the best classifier model

    """
    # ================================================
    # Section 1: Setup and Import Transforms
    # ================================================
    if tform_config_path is None:
        # ALLOWED so we can test functions without Transfoms
        #    If so, create a list of one Tform_config, which will be "None"
        tform_command_list = ["no_transform"]
        tform_command_dict = {"no_transform": None}
    else:
        # Import the Tform Config List (and the dictionary for it)
        tform_command_list, tform_command_dict = \
            arbitrage.import_tform_config(tform_config_path)
        pass
    # ===========================
    # 1b) ANY OTHER SETUP?
    # ===========================

    test_set_filenames = preprocessing.hold_out_test_set(
        raw_datapath, number_of_files_per_class=num_test_files_class,
        classes=classes)

    for tform_name in tform_command_list:

        # ============================================
        # Section 2: Data Wrapper        (Setup + Run)
        # ============================================
        tform_commands = tform_command_dict[tform_name]

        if iterator_mode == 'arrays':
            image_data = data_wrapper(
                raw_datapath, tform_commands=tform_commands,
                plot_format=plot_format, iterator_mode=iterator_mode,
                print_out=print_out, run_name=tform_name, scale=scale,
                project_name=project_name, classes=classes, skiprows=skiprows)
            image_path = None
        else:
            image_data = None
            image_path = data_wrapper(
                raw_datapath, tform_commands=tform_commands,
                plot_format=plot_format, iterator_mode=iterator_mode,
                print_out=print_out, run_name=tform_name, scale=scale,
                project_name=project_name, classes=classes, skiprows=skiprows)

        # ============================================
        # Section 3: Classifier Wrapper  (Setup + Run)
        # ============================================

        # Image PATH is none, but we can pass DATA
        classifier_wrapper(raw_datapath, test_set_filenames,
                           tform_name, classifier_config_path,
                           image_data=image_data,
                           classifier=classifier,
                           iterator_mode=iterator_mode,
                           split=split, color_mode=color_mode,
                           target_size=target_size,
                           batch_size=batch_size,
                           image_path=image_path,
                           classes=classes,
                           project_name=project_name, k_fold=k_fold, k=k)
        # NO OUTPUT? - it outputs the report file

    return None


def data_wrapper(raw_datapath, tform_commands=None, classes=None,
                 plot_format="RGBrgb", iterator_mode='arrays',
                 print_out=True, project_name=None, run_name=None,
                 skiprows=0, scale=1.0):
    """
    Overall "One-Click" Wrapper to create the three "Keras Ready" Datasets
        needed to train the model: "Training Set", "Validation Set" and
        "Test Set", all in the same format which is created via the
        Keras.Preprocessing.Data.Flow (<--- Not exact package/function)

    """
    if print_out:
        clock = time.perf_counter()
        print("Processing Data...\t", end="")
    # Make the raw Dataframe Tuples List
    raw_tuples_list = to_catalogue._data_tuples_from_fnames(
        raw_datapath, classes=classes, skiprows=skiprows)
    # Now perform trasnsform if given
    if tform_commands is None:
        tform_tuples_list = raw_tuples_list
    else:
        tform_tuples_list = arbitrage.tform_tuples(raw_tuples_list,
                                                   tform_commands,
                                                   rgb_format=plot_format)

    # save the tranformation info in a yaml file for final report
    if project_name and run_name:
        output = [[i, name.split('__')[0], name.split('__')[-1]] for
                  i, name in enumerate(list(tform_tuples_list[0][1]))
                  if isinstance(name, str)]
    # save the tranform info in a dictionary
        run_tform = {'run_name': run_name}
        for i in range(len(output)):
            run_tform['tform_' + str(i)] = output[i]
        # generate a yaml file to store the trasnformation info
        output_path = preprocessing.save_to_folder(raw_datapath, project_name,
                                                   run_name)
        report_location = output_path+'/report/'
        if not os.path.exists(report_location):
            os.makedirs(report_location)
        with open(report_location+'run_tform_config.yaml',
                  'w') as yaml_file:
            yaml.dump(run_tform, yaml_file)
            yaml_file.close()
    else:
        pass
    # Next make the rgb images Tuples List
    if plot_format == 'RGBrgb':
        tuples_list = to_catalogue.rgb_list(tform_tuples_list, scale=scale,
                                            plot_format=plot_format)
    else:
        tuples_list = to_catalogue.regular_plot_list(
            tform_tuples_list, scale=scale)

    # OK! Now we have image arrays finished!
    #     EITHER Return that list of image tuples
    #     OR save images and Return the path to those folders!
    if iterator_mode == 'arrays':
        if print_out:
            print_time(time.perf_counter()-clock)
        return tuples_list
    else:
        # Write Optional Split based on Iterator_Mode,
        # to optionally use the "to_dirFlow"
        # path options (Already partly written!)...
        return os.path.join(raw_datapath, "images")


def classifier_wrapper(input_path, test_set_filenames, run_name, config_path,
                       image_data=None, classifier='tuner',
                       iterator_mode='arrays', split=0.1,
                       target_size=(80, 80), color_mode='rgb',
                       batch_size=32, image_path=None,
                       classes=['class_1', 'class_2'],
                       project_name='tuner_run',
                       k_fold=False, k=None, **kwarg):
    '''
    Single "Universal" Wrapping function to setup and run the CNN and Tuner
    on any properly labeled image set.

    Operates in either of two formats:
        "arrays"  : Takes data as "List_of_Image_Tuples"
        "else"    : Takes data as "image_path" of sorted image folders

    Parameters:
    -------------
    input_datapath : str
                   path to the raw .csv files containing the data to classify
    test_set_filenames : list
                         The list containig the strings of filenames
                         randomly selected to be part of the test set.
    config_path : str
                  string containing the path to the yaml file
                  representing the classifier hyperparameters
    run_name : str
               name use to create a folder for storing the results of this run
    iterator_mode : str
                    option to use images from arrays directly or save the
                    .png and use a directory iterator mode
    plot_format : str
                  option for standard or RGB color gradient
    print_out : bool
                option for printing out feedback on conputational time taken to
                initialize the data and generate the images
    num_test_files_class : int or float
                            numebr of files per class to select for the test
                            set
    classifier : str
                  option cnn or tuner
    split : float
            the percentage of the learning set to use for the validation step
    target_size : tuple
                  image target size. Presented as a tuble indicating number of
                  pixels composing the two dimensions of the image (w x h)
    batch_size : int
                 The number of files to group up into a batch

    classes : list
              A list containing strings of the classes the data is divided in.
              The class name represent the folder name the files are contained
              in.
    project_name : str
                   name of the folder to be created for storing the results of
                   the tuning
    '''
    if iterator_mode == 'arrays':

        assert image_data, 'No image_data list provided'

        test_set_list, learning_set_list = to_catalogue.data_set_split(
            image_data, test_set_filenames)

        if k_fold:
            test_set = to_catalogue.test_set(image_list=test_set_list,
                                             target_size=target_size,
                                             classes=classes,
                                             color_mode=color_mode,
                                             iterator_mode='arrays',
                                             batch_size=batch_size)
        else:
            training_set, validation_set = to_catalogue.learning_set(
                image_list=learning_set_list, split=split,
                classes=classes, target_size=target_size,
                iterator_mode='arrays', batch_size=batch_size,
                color_mode=color_mode)

            test_set = to_catalogue.test_set(image_list=test_set_list,
                                             target_size=target_size,
                                             classes=classes,
                                             color_mode=color_mode,
                                             iterator_mode='arrays',
                                             batch_size=batch_size)
    else:

        assert image_path, 'no path to the image folders was provided'

        training_set, validation_set = to_catalogue.learning_set(
            image_path, split=split, target_size=target_size,
            iterator_mode='from_directory', batch_size=batch_size,
            classes=classes)

        test_set = to_catalogue.test_set(image_path, target_size=target_size,
                                         classes=classes,
                                         iterator_mode='from_directory',
                                         batch_size=batch_size)
    if k_fold:
        print('test set : {} batches of {} files'.format(len(test_set),
                                                         batch_size))
    else:
        print('training set : {} batches of {} files'.format(len(training_set),
                                                             batch_size))
        print('validation set : {} batches of {} files'.format(
            len(validation_set), batch_size))
        print('test set : {} batches of {} files'.format(len(test_set),
                                                         batch_size))

    if classifier == 'tuner':
        # warn search_function, 'no search function provided,
        # using default RandomSearch'
        tuner.build_param(config_path)
        output_path = preprocessing.save_to_folder(input_path, project_name,
                                                   run_name)
        tuned_model = tuner.run_tuner(training_set, validation_set,
                                      project_name=output_path)
        model, history, metrics = tuner.best_model(tuned_model, training_set,
                                                   validation_set, test_set)
        conf_matrix, report = cnn.report_on_metrics(model, test_set)
        tuner.report_generation(model, history, metrics, output_path,
                                tuner=tuned_model, save_model=True)
    else:
        if k_fold:

            assert k, 'the number of folds needs to be provided'
            validation_score, model, history, final_score = \
                cnn.k_fold_model(k, config_path=config_path,
                                 target_size=target_size,
                                 classes=classes, batch_size=batch_size,
                                 color_mode=color_mode,
                                 iterator_mode=iterator_mode,
                                 image_list=learning_set_list,
                                 test_set=test_set)
            output_path = preprocessing.save_to_folder(input_path,
                                                       project_name,
                                                       run_name)
            conf_matrix, report = cnn.report_on_metrics(model, test_set)
            tuner.report_generation(model, history, final_score, output_path,
                                    tuner=None, save_model=True,
                                    config_path=config_path, k_fold=k_fold,
                                    k=k)

        else:
            model, history = cnn.build_model(training_set, validation_set,
                                             config_path=config_path)
            metrics = cnn.evaluate_model(model, test_set)

            output_path = preprocessing.save_to_folder(input_path,
                                                       project_name,
                                                       run_name)
            conf_matrix, report = cnn.report_on_metrics(model, test_set)
            tuner.report_generation(model, history, metrics, output_path,
                                    tuner=None, save_model=True,
                                    config_path=config_path)

    performance_evaluation = reporting.model_analysis(model, test_set,
                                                      test_set_list)
    performance_evaluation.to_csv(
        output_path+'report/model_evaluation.csv')
    return


def print_time(duration):
    """
    Function to print the time elapsed for the most recent step,
    given the current time
    """

    if duration < 1:
        print("That Took {} mS  !".format(round(duration*1000, 2)))
    elif duration < 60:
        print("That Took {} Sec !".format(round(duration, 2)))
    elif duration < 3600:
        print("That Took {} Min !".format(round(duration/60, 2)))
    else:
        print("That Took {} Hrs !".format(round(duration/3600, 2)))
    return duration
