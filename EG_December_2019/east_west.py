import popgen as pg
import random
import tqdm



# run a single iteration of the simulation, given a set of command line
# arguments, and write results to a file
def do_simulation_file(args):

    east_allele = pg.Allele('E', args.east_fitness)
    west_allele = pg.Allele('W', args.west_fitness)

    east_population = []
    for _ in range(args.east_population):
        east_population.append(pg.Individual([east_allele]))

    west_population = []
    for _ in range(args.west_population):
        west_population.append(pg.Individual([west_allele]))



    with open(args.output_filepath, 'w') as output:

        # write output CSV header line
        if args.output_format == 'frequency':
            output.write('generation,east population size,west population size,east population frequency,west population frequency\n')
        elif args.output_format == 'count':
            output.write('generation,east population size,west population size,east population count,west population count\n')


        if args.progress:
            my_iterator = tqdm.tqdm(range(args.generations), unit='generations')
        else:
            my_iterator = range(args.generations)

        for generation in my_iterator:
            pg.death(east_population)
            pg.death(west_population)

            pg.migration(east_population, west_population)
            pg.migration(west_population, east_population)

            pg.birth(east_population, args.east_population)
            pg.birth(west_population, args.west_population)

            if args.output_format == 'frequency':
                east_output = pg.frequency(east_population, east_allele)
                west_output = pg.frequency(west_population, east_allele)
            elif args.output_format == 'count':
                east_output = round(pg.frequency(east_population, east_allele) * len(east_population))
                west_output = round(pg.frequency(west_population, east_allele) * len(west_population))


            fields = [
                generation,
                len(east_population),
                len(west_population),
                east_output,
                west_output
            ]

            # write one line of the CSV file by joining together fields
            # with comma. Use map() to change to strings first.
            output.write(','.join(map(str, fields)) + '\n')


# run a single iteration of the simluation, given an args object
# and a population size. Return a tuple of (population size, east frequency, west frequency) 
def do_simulation_return(args, east_population_size):

    print(f'running simulation with {east_population_size}')

    east_allele = pg.Allele('E', args.east_fitness)
    west_allele = pg.Allele('W', args.west_fitness)

    east_population = []
    for _ in range(east_population_size):
        east_population.append(pg.Individual([east_allele]))

    west_population = []
    for _ in range(args.west_population):
        west_population.append(pg.Individual([west_allele]))

    my_iterator = range(args.generations)

    for generation in my_iterator:
        pg.death(east_population)
        pg.death(west_population)

        pg.migration(east_population, west_population)
        pg.migration(west_population, east_population)

        pg.birth(east_population, east_population_size)
        pg.birth(west_population, args.west_population)


    east_output = pg.frequency(east_population, east_allele)
    west_output = pg.frequency(west_population, east_allele)

    return(east_population_size, east_output, west_output)




# two functions that check for bounds on numerical inputs
def check_positive_integer(string):
    result = int(string)
    if result < 1:
        raise argparse.ArgumentTypeError('Number of generations and population sizes must all be positive')
    return result

def check_fitness(string):
    result = float(string)
    if not 0 < result < 1:
        raise argparse.ArgumentTypeError('Fitness score must be between zero and one')
    return result

# set up command line argument parsing
import argparse
parser = argparse.ArgumentParser()

parser.add_argument(
    '-o',
    '--output_filepath',
    help = 'the path to the output file (may be just a file name). This will be a CSV format file. (default: output.csv)',
    default = 'output.csv',
)

parser.add_argument(
       '-g',
       '--generations',
       help = 'The number of generations to run the simulation for',
       default = 100,
       type = check_positive_integer
)

parser.add_argument(
       '-ep',
       '--east_population',
       help = 'The size of the east population',
       default = list(range(1001, 100, -100)),
       nargs='+',
       type = check_positive_integer
)

parser.add_argument(
       '-wp',
       '--west_population',
       help = 'The size of the west population',
       default = 100,
       type = check_positive_integer
)

parser.add_argument(
       '-ef',
       '--east_fitness',
       help = 'The fitness of the startin allele in the east population',
       default = 0.8,
       type = check_fitness
)

parser.add_argument(
       '-wf',
       '--west_fitness',
       help = 'The fitness of the starting allele in the west population',
       default = 0.8,
       type = check_fitness
    )

parser.add_argument(
     '-p',
     '--progress',
     help = 'display a progress bar while the simulation is running',
     action = 'store_true'
)

parser.add_argument(
      '-of',
      '--output_format',
      help = 'whether to output allele frequencies or counts',
      default = 'frequency',
      choices = ['frequency', 'count']
)

parser.add_argument(
    '-c',
    '--cores',
    help = 'how many cores to run on',
    type=int,
    default = 1

)

args = parser.parse_args()

# simulation code starts here

# helper function to take a single population size, add the args object and call the simulation function
def helper(east_population_size):
    return do_simulation_return(args, east_population_size)


import multiprocessing

# set up a pool of Python processes to do the simulations 
pool = multiprocessing.Pool(args.cores)

# we get the results by mapping the helper function over the list of population sizes we want to test
summary = pool.map(helper, args.east_population)

print(list(summary))
