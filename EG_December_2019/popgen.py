import random

class Allele:
    def __init__(self, name, fitness):
        self.name = name
        self.fitness = fitness

    def __repr__(self):
        return f'I am an allele called {self.name} with fitness {self.fitness}'

class Individual:

    fitness = None

    def __init__(self, alleles):
        self.alleles = alleles


    def get_genotype(self):
        result = ''
        for allele in self.alleles:
            result = result + allele.name
        return result

    def get_fitness(self):
        result = 1
        for allele in self.alleles:
            result = result * allele.fitness
        return result

    def get_fitness_backup(self):
        if self.fitness is None:
            self.fitness = self._get_fitness()
        return self.fitness

    def __repr__(self):
        return f'Individual with genotype {self.get_genotype()}'


def create_random_individual():
    my_random_alleles = [
        random.choice(locus_one),
        random.choice(locus_two),
        random.choice(locus_three),
    ]
    return Individual(my_random_alleles)

def frequency(population, a):
    count = 0
    for i in population:
        if a in i.alleles:
            count = count + 1

    return count / len(population)

#@profile
def death_2(population):
    new_population =[]
    for individual in population:
        cutoff =  random.random()
        if individual.get_fitness() > cutoff:
            new_population.append(individual)
    population = new_population

def death(population):
    for individual in population:
        if individual.get_fitness() < random.random():
            population.remove(individual)



def birth(population, desired_size):
    for _ in range(desired_size - len(population)):
        chosen_one = random.choice(population)
        offspring = Individual(chosen_one.alleles)
        population.append(offspring)


def migration(from_pop, to_pop):
        migrant = random.choice(from_pop)
        from_pop.remove(migrant)
        to_pop.append(migrant)
