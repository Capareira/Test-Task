import logging
import hashlib
import os
import shutil
import sys
import time

def logging_setup(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S');

def calculate_MD5(file):
    md5 = hashlib.md5();
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk);
    return md5.hexdigest();

def sync(source, replica):

    if not os.path.exists(source):
        logging.error('Source does not exist');
        print('Source does not exist');
        print('Closing program...');
        sys.exit(1);
        return False;

    if not os.path.exists(replica):
        logging.error('Replica does not exist');
        print('Replica does not exist');
        print('Closing program...');
        sys.exit(1);
        return False;

    for current_path, _, files in os.walk(source): #Iterates source folder
        rel_path = os.path.relpath(current_path, source);
        replica_directory = os.path.join(replica, rel_path);

        if not os.path.exists(replica_directory): #Creates a replica directory if it does not exist
            os.makedirs(replica_directory);
            logging.info('Replica directory created');
            print('Replica directory created in %s' % replica_directory);

    for file in files:
        source_file = os.path.join(current_path, file);
        replica_file = os.path.join(replica_directory, file);

        if not os.path.exists(replica_file) or calculate_MD5(source_file) != calculate_MD5(replica_file):
            shutil.copy2(source_file, replica_file);
            logging.info('File copied or updated: %s', file);
            print('File copied or updated: %s' % file);


    for current_path, _, files in os.walk(replica, topdown=False): #topdown is false to remove directories first
        rel_path = os.path.relpath(current_path, replica);
        source_directory = os.path.join(source, rel_path);

        if not os.path.exists(source_directory):
            shutil.rmtree(current_path);
            logging.info('Replica directory deleted');
            print('Replica directory removed from %s' % current_path);

            continue

        for file in files:
            replica_file = os.path.join(current_path, file);
            source_file = os.path.join(source_directory, file);

            if not os.path.exists(source_file):
                os.remove(replica_file);
                logging.info('File deleted: %s', file);
                print('File deleted: %s' % file);


def main(source, replica, sync_period, log_file):

    logging_setup(log_file);
    logging.info('Sync started...');
    print('Sync started...');


    while True:
        sync(source, replica);
        logging.info('Sync finished. Next sync in %s seconds', sync_period);
        print('Sync finished! Next sync in %s seconds...' % sync_period);
        time.sleep(sync_period);

if __name__ == '__main__':

    if len(sys.argv) != 5:
        print('Invalid number of Arguments!');
        print('Usage: python sync.py "<source_folder>" "<replica_folder>" <sync_period> "<log_file>"');
        sys.exit(1);

    source_folder = sys.argv[1];
    replica_folder = sys.argv[2];
    sync_period = int(sys.argv[3]);
    log_file = sys.argv[4];

    main(source_folder, replica_folder, sync_period, log_file);