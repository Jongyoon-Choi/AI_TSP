import random
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from utils import save_csv
from argparse import ArgumentParser
from genetic_algorithm.chromosome import Chromosome
from genetic_algorithm.order import order_crossover
from genetic_algorithm.position_based import position_based_crossover
from genetic_algorithm.uniform_order_based import uniform_order_based_crossover
from genetic_algorithm.PMX import pmx_crossover
from genetic_algorithm.cycle import cycle_crossover
from genetic_algorithm.mutation import mutate

def print_p(pop):
    i = 0
    for x in pop:
        # print(f"염색체 #{i} = {x.genes} 적합도={x.fitness:.2f}")
        print(f"염색체 #{i} 적합도={x.fitness:.2f}")
        i += 1
    print("")

def main(): # 메인 프로그램
    parser = ArgumentParser()

    parser.add_argument("--POPULATION_SIZE", type=int, default=50, help="Population size")
    parser.add_argument("--MUTATION_RATE", type=float, default=0.01, help="Mutation rate")
    parser.add_argument("--SIZE", type=int, default=998, help="Number of genes in a chromosome")
    parser.add_argument("--MAX_VAL", type=float, default=420, help="Maximum fitness value")
    parser.add_argument("--iteration", type=int, default=500, help="Number of iterations")
    parser.add_argument("--crossover_name", type=str, default="cycle", help="Name of crossover function")
    parser.add_argument("--output_path", type=str, default="GA_result/test", help="output path")

    args = parser.parse_args()

    # 랜덤 시드 설정
    random.seed(42)

    POPULATION_SIZE = args.POPULATION_SIZE	# 개체 집단의 크기
    MUTATION_RATE = args.MUTATION_RATE	# 돌연 변이 확률
    SIZE = args.SIZE			# 하나의 염색체에서 유전자 개수		
    MAX_VAL = args.MAX_VAL
    
    crossover_functions = {
        'order': order_crossover,
        'position_based': position_based_crossover,
        'uniform_order_based': uniform_order_based_crossover,
        'pmx': pmx_crossover,
        'cycle': cycle_crossover,
    }
    
    population = []
    fitness_list = []

    # 초기 염색체를 생성하여 객체 집단에 추가한다. 
    num_rand = int(POPULATION_SIZE * 0.3)

    for _ in range(num_rand):
        population.append(Chromosome(size = SIZE, MAX_VAL= MAX_VAL))

    for i in range(POPULATION_SIZE-num_rand):
        population.append(Chromosome(num_chunk = i + 1 ,size = SIZE, MAX_VAL= MAX_VAL))

    # 적합도 낮은 순 정렬
    population.sort(key=lambda x: x.cal_fitness())

    # #출력
    # print("세대 번호=", 0)
    # print_p(population)

    # population의 평균 fitness 계산
    sum_fitness = 0
    for c in population:
        sum_fitness += c.fitness
    
    avg_fitness =  sum_fitness/POPULATION_SIZE

    fitness_list.append(avg_fitness)

    # min_fitness 초기화
    min_fitness = 1000

    for i in tqdm(range(args.iteration), desc='Progress'):  # 진행률 표시
    # for i in range(args.iteration):   # 진행률 표시 X
        # MUTATION_RATE 감소
        if population[0].fitness < min_fitness:
            MUTATION_RATE = MUTATION_RATE * 0.9
            min_fitness = population[0].fitness

        new_pop = [] 

        # 선택과 교차 연산
        for _ in range(POPULATION_SIZE//2): 
            c1, c2 = crossover_functions[args.crossover_name](population)
            new_pop.append(Chromosome(c1))
            new_pop.append(Chromosome(c2))

        # 자식 세대가 부모 세대를 대체한다. 
        parent_pop = [c for c in population]
        for c in new_pop:
            if c not in parent_pop:
                population.pop()
                population.insert(0,c)

        # 돌연변이 연산
        for c in population: mutate(c, MUTATION_RATE)

        # 출력을 위한 정렬
        population.sort(key=lambda x: x.cal_fitness())
        
        # population의 평균 fitness 계산
        sum_fitness = 0
        for c in population:
            sum_fitness += c.fitness
        
        avg_fitness =  sum_fitness/POPULATION_SIZE

        fitness_list.append(avg_fitness)
        # fitness_list.append(population[0].fitness)

        # #출력
        # print("세대 번호=", i+1)
        # print_p(population)

    # csv 파일로 저장
    sol=[0]+population[0].genes

    save_csv(sol, f'solutions/GA_Astar_solution.csv')

    # cost 출력
    print(f'final cost: {population[0].fitness:.2f}')


    # 시각화
    # fitness_list=fitness_list[10:]
    x, y = range(len(fitness_list)),fitness_list
    fit_line = np.polyfit(x,y,1)
    x_minmax = np.array([min(x), max(x)])
    fit_y = x_minmax * fit_line[0] + fit_line[1]

    plt.plot(fitness_list,label='fitness')
    plt.plot(x_minmax, fit_y, color = 'red',label='regression')
    plt.text(0.5, 0.9, f'Regression: y = {fit_line[0]:.5f}x + {fit_line[1]:.2f}', 
            horizontalalignment='center', verticalalignment='center', 
            transform=plt.gca().transAxes, fontsize=10, color='red')
    plt.xlabel('generation number')
    plt.ylabel('fitness')
    plt.legend()
    # plt.show()

    # 이미지 파일로 저장
    plt.savefig(f'{args.output_path}.png')

if __name__ == "__main__":
    main()