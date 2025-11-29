// ga_cli.cpp
// Compile: g++ -O3 -std=c++17 ga_cli.cpp -o ga_cli
// Example run (no logs): ./ga_cli 6 8 5 4
// Example run (with logs): ./ga_cli 6 8 5 4 --verbose
//
// NOTES:
// - All human logs are written to stderr (cerr).
// - Final JSON is printed to stdout (cout) only — safe for subprocess parsing.

#include <bits/stdc++.h>
using namespace std;

using vi = vector<int>;
using vd = vector<double>;
using population_element = pair<vi, double>;

static std::mt19937 rng((uint32_t)chrono::high_resolution_clock::now().time_since_epoch().count());

double fitness_function(double C, double g, double x, double c) {
    if (C <= 0.0) return 1e18;
    double ratio = g / C;
    double a = (1.0 - ratio);
    a = a * a;

    double p = 1.0 - (ratio * x);
    if (p <= 1e-9) {
        return 1e12 + fabs(p) * 1e6;
    }

    double d1i = (0.38 * C * a) / p;
    double a2 = 173.0 * (x * x);
    double rad = (x - 1.0) + (x - 1.0) * (x - 1.0) + ((16.0 * x) / c);
    if (rad < 0.0) rad = 0.0;
    double ri1 = sqrt(rad);
    double d2i = a2 * ri1;
    return d1i + d2i;
}

vector<population_element> initialize_population(int pop_size, int num_lights,
                                                int green_min, int green_max,
                                                int cycle_time, const vi &cars) {
    vector<population_element> population;
    population.reserve(pop_size);

    vi road_capacity(num_lights, 20);
    vd road_congestion(num_lights);
    for (int i = 0; i < num_lights; ++i) {
        road_congestion[i] = double(road_capacity[i] - cars[i]) / double(road_capacity[i]);
    }

    uniform_int_distribution<int> green_dist(green_min, green_max);

    int attempts = 0;
    while ((int)population.size() < pop_size && attempts < pop_size * 1000) {
        ++attempts;
        vi green_times(num_lights);
        int sum = 0;
        for (int i = 0; i < num_lights; ++i) {
            green_times[i] = green_dist(rng);
            sum += green_times[i];
        }
        if (sum <= cycle_time) {
            double total_delay = 0.0;
            for (int i = 0; i < num_lights; ++i) {
                total_delay += fitness_function((double)cycle_time, (double)green_times[i],
                                               road_congestion[i], (double)road_capacity[i]);
            }
            population.emplace_back(move(green_times), total_delay);
        }
    }

    sort(population.begin(), population.end(),
         [](const population_element &a, const population_element &b){ return a.second < b.second; });

    return population;
}

int roulette_wheel_selection(const vector<population_element> &population, double beta) {
    int n = (int)population.size();
    if (n == 0) return 0;
    vector<double> delays(n);
    for (int i = 0; i < n; ++i) delays[i] = population[i].second;
    double worst = *max_element(delays.begin(), delays.end());
    vector<double> weights(n);
    double sumw = 0.0;
    if (worst <= 0.0) {
        for (int i = 0; i < n; ++i) weights[i] = 1.0, sumw += 1.0;
    } else {
        for (int i = 0; i < n; ++i) {
            double w = exp(-beta * delays[i] / worst);
            weights[i] = w;
            sumw += w;
        }
        if (sumw <= 0.0) {
            for (int i = 0; i < n; ++i) weights[i] = 1.0;
            sumw = n;
        }
    }
    discrete_distribution<int> dd(weights.begin(), weights.end());
    return dd(rng);
}

pair<vi,vi> crossover(const vi &p1, const vi &p2) {
    int num_lights = (int)p1.size();
    if (num_lights <= 1) return {p1, p2};
    uniform_int_distribution<int> point_dist(1, num_lights - 1);
    int point = point_dist(rng);
    vi c1(num_lights), c2(num_lights);
    for (int i = 0; i < num_lights; ++i) {
        if (i < point) { c1[i] = p1[i]; c2[i] = p2[i]; }
        else { c1[i] = p2[i]; c2[i] = p1[i]; }
    }
    return {c1, c2};
}

vi mutate(const vi &individual, double mutation_rate, int green_min, int green_max) {
    int num_lights = (int)individual.size();
    vi mutated = individual;
    int nmuts = int(mutation_rate * num_lights);
    if (nmuts <= 0) return mutated;

    uniform_int_distribution<int> idx_dist(0, num_lights - 1);
    uniform_int_distribution<int> sign_dist(0,1);
    double sigma_base = 0.02 * double(green_max - green_min);

    for (int k = 0; k < nmuts; ++k) {
        int idx = idx_dist(rng);
        int sign = sign_dist(rng) ? 1 : -1;
        double sigma = sign * sigma_base;
        int delta = int(round(sigma));
        int newv = mutated[idx] + delta;
        if (newv < green_min) newv = green_min;
        if (newv > green_max) newv = green_max;
        mutated[idx] = newv;
    }
    return mutated;
}

vi inversion(vi individual) {
    int num_lights = (int)individual.size();
    if (num_lights < 2) return individual;
    uniform_int_distribution<int> iddist(0, num_lights - 1);
    int i1 = iddist(rng);
    int i2 = iddist(rng);
    if (i1 > i2) swap(i1, i2);
    reverse(individual.begin() + i1, individual.begin() + i2 + 1);
    return individual;
}

pair<population_element, vector<double>> genetic_algorithm(int pop_size, int num_lights, int max_iter,
                                              int green_min, int green_max, int cycle_time,
                                              double mutation_rate, double pinv, double beta,
                                              const vi &cars, bool verbose=false) {
    vector<population_element> population = initialize_population(pop_size, num_lights, green_min, green_max, cycle_time, cars);
    if (population.empty()) {
        vi fallback(num_lights, green_min);
        double d = 0.0;
        for (int i = 0; i < num_lights; ++i)
            d += fitness_function((double)cycle_time, (double)fallback[i],
                                  double((20 - cars[i]))/20.0, 20.0);
        population.emplace_back(fallback, d);
        if (verbose) cerr << "[init] fallback population created\n";
    }

    if ((int)population.size() > pop_size) population.resize(pop_size);

    population_element best_sol = population.front();
    vector<double> best_delays;
    best_delays.reserve(max_iter + 1);
    best_delays.push_back(best_sol.second);

    vi road_capacity(num_lights, 20);
    vector<double> road_congestion(num_lights);
    for (int i = 0; i < num_lights; ++i) road_congestion[i] = double(road_capacity[i] - cars[i]) / double(road_capacity[i]);

    if (verbose) {
        cerr << "[ga] pop_size=" << pop_size
             << " max_iter=" << max_iter
             << " green_min=" << green_min
             << " green_max=" << green_max
             << " cycle_time=" << cycle_time << "\n";
        cerr << "[ga] starting best delay=" << best_sol.second << "\n";
    }

    for (int iter = 0; iter < max_iter; ++iter) {
        vector<population_element> new_population;
        new_population.reserve(pop_size);

        while ((int)new_population.size() < pop_size) {
            int i1 = roulette_wheel_selection(population, beta);
            int i2 = roulette_wheel_selection(population, beta);
            const vi &parent1 = population[i1].first;
            const vi &parent2 = population[i2].first;

            auto pr = crossover(parent1, parent2);
            vi child1 = pr.first;
            vi child2 = pr.second;

            if (accumulate(child1.begin(), child1.end(), 0) <= cycle_time) {
                child1 = mutate(child1, mutation_rate, green_min, green_max);
                for (int i = 0; i < num_lights; ++i) {
                    if (child1[i] < green_min) child1[i] = green_min;
                    if (child1[i] > green_max) child1[i] = green_max;
                }
                double total_delay = 0.0;
                for (int i = 0; i < num_lights; ++i)
                    total_delay += fitness_function((double)cycle_time, (double)child1[i], road_congestion[i], (double)road_capacity[i]);
                new_population.emplace_back(move(child1), total_delay);
            }

            if ((int)new_population.size() >= pop_size) break;

            if (accumulate(child2.begin(), child2.end(), 0) <= cycle_time) {
                child2 = mutate(child2, mutation_rate, green_min, green_max);
                for (int i = 0; i < num_lights; ++i) {
                    if (child2[i] < green_min) child2[i] = green_min;
                    if (child2[i] > green_max) child2[i] = green_max;
                }
                double total_delay = 0.0;
                for (int i = 0; i < num_lights; ++i)
                    total_delay += fitness_function((double)cycle_time, (double)child2[i], road_congestion[i], (double)road_capacity[i]);
                new_population.emplace_back(move(child2), total_delay);
            }
        }

        int tries = 0;
        while ((int)new_population.size() < pop_size && tries < pop_size * 5) {
            ++tries;
            uniform_int_distribution<int> pick(0, (int)population.size() - 1);
            vi individual = inversion(population[pick(rng)].first);
            if (accumulate(individual.begin(), individual.end(), 0) <= cycle_time) {
                individual = mutate(individual, mutation_rate, green_min, green_max);
                double total_delay = 0.0;
                for (int i = 0; i < num_lights; ++i)
                    total_delay += fitness_function((double)cycle_time, (double)individual[i], road_congestion[i], (double)road_capacity[i]);
                new_population.emplace_back(move(individual), total_delay);
            }
        }

        for (auto &e : new_population) population.push_back(move(e));
        sort(population.begin(), population.end(), [](const population_element &a, const population_element &b){ return a.second < b.second; });
        if ((int)population.size() > pop_size) population.resize(pop_size);

        if (population.front().second < best_sol.second) {
            best_sol = population.front();
            if (verbose) {
                cerr << "[iter " << iter+1 << "] new best delay = " << best_sol.second
                     << "  green = [" << best_sol.first[0] << "," << best_sol.first[1]
                     << "," << best_sol.first[2] << "," << best_sol.first[3] << "]\n";
            }
        } else {
            if (verbose) {
                cerr << "[iter " << iter+1 << "] best delay = " << best_sol.second << "\n";
            }
        }
        best_delays.push_back(best_sol.second);
    }

    return {best_sol, best_delays};
}

int main(int argc, char** argv) {
    if (argc < 5) {
        cerr << "{\"error\":\"Usage: ga_cli north south west east [--verbose|-v]\"}\n";
        return 1;
    }

    bool verbose = false;
    for (int i = 5; i < argc; ++i) {
        string s = argv[i];
        if (s == "-v" || s == "--verbose") verbose = true;
    }

    if (argc == 6) {
        string maybe = argv[5];
        if (maybe == "-v" || maybe == "--verbose") verbose = true;
    }

    vi cars(4);
    for (int i = 0; i < 4; ++i) {
        try {
            cars[i] = stoi(string(argv[i+1]));
            if (cars[i] < 0) cars[i] = 0;
        } catch (...) { cars[i] = 0; }
    }

    int pop_size = 400;
    int num_lights = 4;
    int max_iter = 25;
    int green_min = 10;
    int green_max = 60;
    int cycle_time = 160 - 12;
    double mutation_rate = 0.02;
    double pinv = 0.2;
    double beta = 8.0;

    if (verbose) {
        cerr << "ga_cli starting with cars = [" << cars[0] << "," << cars[1] << "," << cars[2] << "," << cars[3] << "]\n";
    }

    auto res = genetic_algorithm(pop_size, num_lights, max_iter, green_min, green_max, cycle_time, mutation_rate, pinv, beta, cars, verbose);
    population_element best = res.first;

    // Final JSON on stdout only
    cout << "{\"north\":" << best.first[0]
         << ",\"south\":" << best.first[1]
         << ",\"west\":"  << best.first[2]
         << ",\"east\":"  << best.first[3]
         << ",\"delay\":" << best.second
         << "}\n";

    if (verbose) {
        // also print a short summary to stderr
        cerr << "GA finished. Final best delay = " << best.second << "\n";
        cerr << "Final greens: N=" << best.first[0] << " S=" << best.first[1]
             << " W=" << best.first[2] << " E=" << best.first[3] << "\n";
    }

    return 0;
}
