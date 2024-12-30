# Examples:
# python3 ./manage_media.py --source '/backup/camera/*.MTS' --target /backup/x --do-it
# python3 /home/halley/scripts/manage_media.py --source '/backup/media/_/*' --target /backup/media --do-it
import click
import glob
import subprocess
import re
import os
from datetime import datetime
from dateutil import parser


def normalize_date(date_string):
    return re.sub(r"^(\d{4}):(\d{2}):(\d{2})", r"\1-\2-\3", date_string)

def convert_line_to_datetime(line):
    clean_string = ':'.join(line.split(':')[1:]).strip()
    # print(f"{clean_string}")
    if (clean_string == "0000:00:00 00:00:00"):
        return datetime.fromtimestamp(0)
    parsed_date = parser.parse(normalize_date(clean_string));
    #print(f"{parsed_date} #");

    return parsed_date

def get_create_datetime(exif_output):
    headers = ['Date/Time Original', 'Media Create Date', 'File Modification Date/Time']
    lines = exif_output.split('\n')
    dates = {}
    for line in lines:
        for header in headers:
            if line.startswith(header):
                dates[header] = convert_line_to_datetime(line)
    for header in headers:
        if header in dates:
            return dates[header]

    raise Exception('\n'.join(lines))

def get_file_size(filename):
    file_stats = os.stat(filename)
    return file_stats.st_size

@click.command()
@click.option('--source', '-s', required=True)
@click.option('--target', '-t', required=True)
@click.option('--do-it', is_flag=True)
def main(source, target, do_it):
    counter = 0
    for current_file in glob.glob(source):
        counter = counter+1;
        print(counter)
        proc = subprocess.Popen(['exiftool', current_file], stdout=subprocess.PIPE)
        out = proc.communicate()[0]
        if proc.returncode != 0:
            print('Error: {}'.format(current_file))
            continue
        create_datetime = get_create_datetime(out.decode("utf-8", errors='ignore'))
        create_datetime_string = create_datetime.strftime('%Y/%m-%d')

        target_dir = '{}/{}'.format(target, create_datetime_string)
        current_file_target_full_path = '{}/{}'.format(target_dir, os.path.basename(current_file))
        current_file_target_exists = os.path.isfile(current_file_target_full_path)
        if current_file_target_exists:
            current_file_target_size = get_file_size(current_file_target_full_path);
            current_file_size = get_file_size(current_file);
            if (current_file_size == current_file_target_size):
                print(f'No action, duplicate: {current_file}, {current_file_target_full_path}');
                continue
            print("Duplicate, size no differs");
            print(current_file_size);
            print(current_file_target_size);
            print(current_file_target_full_path);
            print(current_file);
            exit();
            print('File exists: {file}, date: {date}, {current_file_target_full_path}'.format(file=current_file, date=create_datetime_string, current_file_target_full_path=current_file_target_full_path))
        else:
            if do_it:
                subprocess.run(['mkdir', '-p', target_dir])
                subprocess.run([
                    'mv',
                    '-n',
                    current_file,
                    target_dir
                ])
            print('Done: {file}, date: {date}'.format(file=current_file, date=create_datetime_string))

main()
