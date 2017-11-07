import csv

def load_policy(file_location):
    policy = {}
    with open(file_location) as csvfile:
        reader = csv.reader(csvfile, dialect='excel')
        for row in reader:
            clean_params = []
            for element in row[1:]:
                if element != '':
                    clean_params.append(float(element))
            if len(clean_params) == 1:
                clean_params = clean_params[0]
            policy[row[0]] = clean_params
    return policy


def load_taxpayers(file_location):
    taxpayers = []
    with open(file_location) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel')
        for row in reader:
            for key in row:
                row[key] = int(row[key])
            taxpayers.append(row)
    return taxpayers

def write_results(results_list, results_file): 
    try:
        with open(results_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=results_list[0].keys(), dialect='excel')
                writer.writeheader()
                for row in results_list:
                    writer.writerow(row)
    except PermissionError:
        print("PermissionError: Results file in use. Please close '" + results_file + "' and try again.")
