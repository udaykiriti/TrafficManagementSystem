#include <bits/stdc++.h>
#ifdef _OPENMP
#include <omp.h>
#endif
using namespace std;

using vi = vector<int>;
using population_element = pair<vi, double>;
#define FOR(i,a,b) for(int i = a ; i < b ; i++)

static std::mt19937 rng(
    (uint32_t)chrono::high_resolution_clock::now().time_since_epoch().count());

/*<---- Per-light precomputed constants ---->*/
struct LightConstants 
{
  double x;      /* <- road_congestion -> */
  double c;      /* <- road-capacity -> */
  double a2_ri1; // precomputed 173 * (x^2) * sqrt((x - 1) + (x - 1)^2 + (16 * // x) / c)
};
/*function that helps to split time base on their req*/
double fitness_function(double C, double g, const LightConstants &lc) 
{
  if (C <= 0.0)
  {
    return 1e18;
  }
  double ratio = g / C;
  double a = (1.0 - ratio);
  a *= a;

  double p = 1.0 - (ratio * lc.x);
  if (p <= 1e-9) 
  {
    return 1e12 + fabs(p) * 1e6;
  }

  double d1i = (0.38 * C * a) / p;
  return d1i + lc.a2_ri1;
}

/* <---  Function to normalize green times to fit cycle_time so it can redistibure ---> */
void normalize_greens(vi &greens, int cycle_time, int green_min,
                      int green_max) {
  int sum = accumulate(greens.begin(), greens.end(), 0);
  if (sum <= cycle_time)
  {
    return;
  }

  double scale = (double)cycle_time / sum;
  int new_sum{0};
  int tmp =int(greens.size());
  FOR (i,0,tmp) 
  {
    greens[i] = max(green_min, min(green_max, (int)(greens[i] * scale)));
    new_sum += greens[i];
  }

  // Distribute remaining budget or trim excess among those 
  int idx = 0;
  while (new_sum > cycle_time) 
  {
    if (greens[idx] > green_min) 
    {
      greens[idx]--;
      new_sum--;
    }
    idx = (idx + 1) % greens.size();
  }
}

vector<population_element>
initialize_population(int pop_size, int num_lights, int green_min,
                      int green_max, int cycle_time,
                      const vector<LightConstants> &lcs) {
  vector<population_element> population;
  population.reserve(pop_size);

  uniform_int_distribution<int> green_dist(green_min, green_max);

  int attempts = 0;
  while ((int)population.size() < pop_size && attempts < pop_size * 1000) {
    ++attempts;
    vi green_times(num_lights);
    for (int i = 0; i < num_lights; ++i) {
      green_times[i] = green_dist(rng);
    }

    normalize_greens(green_times, cycle_time, green_min, green_max);

    double total_delay = 0.0;
    for (int i = 0; i < num_lights; ++i) {
      total_delay +=
          fitness_function((double)cycle_time, (double)green_times[i], lcs[i]);
    }
    population.emplace_back(std::move(green_times), total_delay);
  }

  sort(population.begin(), population.end(),
       [](const population_element &a, const population_element &b) {
         return a.second < b.second;
       });

  return population;
}

struct SelectionInfo {
  discrete_distribution<int> dist;
};

SelectionInfo prepare_selection(const vector<population_element> &population,double beta) {
  int n = (int)population.size();
  if (n == 0)
    return {};

  double min_delay = population.front().second;
  double worst = population.back().second;
  vector<double> weights(n);

  if (worst <= min_delay) {
    fill(weights.begin(), weights.end(), 1.0);
  } else {
    for (int i = 0; i < n; ++i) {
      weights[i] =
          exp(-beta * (population[i].second - min_delay) / (worst - min_delay));
    }
  }
  return {discrete_distribution<int>(weights.begin(), weights.end())};
}

int roulette_wheel_selection(const SelectionInfo &info, mt19937 &local_rng) {
  return const_cast<discrete_distribution<int> &>(info.dist)(local_rng);
}

pair<vi, vi> crossover(const vi &p1, const vi &p2, mt19937 &local_rng) {
  int num_lights = (int)p1.size();
  if (num_lights <= 1)
    return {p1, p2};
  uniform_int_distribution<int> point_dist(1, num_lights - 1);
  int point =
      point_dist(rng); // using global rng for simplicity or local_rng if needed
  vi c1 = p1, c2 = p2;
  for (int i = point; i < num_lights; ++i) {
    swap(c1[i], c2[i]);
  }
  return {c1, c2};
}

vi mutate(vi mutated, double mutation_rate, int green_min, int green_max,
          mt19937 &local_rng) {
  int num_lights = (int)mutated.size();
  uniform_real_distribution<double> prob_dist(0.0, 1.0);
  uniform_int_distribution<int> sign_dist(0, 1);
  double sigma_base = 0.02 * double(green_max - green_min);

  for (int i = 0; i < num_lights; ++i) {
    if (prob_dist(local_rng) < mutation_rate) {
      int sign = sign_dist(local_rng) ? 1 : -1;
      int delta = int(round(sign * sigma_base));
      mutated[i] = max(green_min, min(green_max, mutated[i] + delta));
    }
  }
  return mutated;
}

vi inversion(vi individual, mt19937 &local_rng) {
  int num_lights = (int)individual.size();
  if (num_lights < 2)
    return individual;
  uniform_int_distribution<int> iddist(0, num_lights - 1);
  int i1 = iddist(local_rng);
  int i2 = iddist(local_rng);
  if (i1 > i2)
    swap(i1, i2);
  reverse(individual.begin() + i1, individual.begin() + i2 + 1);
  return individual;
}

pair<population_element, vector<double>>
genetic_algorithm(int pop_size, int num_lights, int max_iter, int green_min,
                  int green_max, int cycle_time, double mutation_rate,
                  double beta, const vector<LightConstants> &lcs,
                  bool verbose = false) {
  vector<population_element> population = initialize_population(
      pop_size, num_lights, green_min, green_max, cycle_time, lcs);

  population_element best_sol = population.front();
  vector<double> best_delays;
  best_delays.reserve(max_iter + 1);
  best_delays.push_back(best_sol.second);

  if (verbose) {
    cerr << "[ga] pop_size=" << pop_size << " max_iter=" << max_iter
         << " green_min=" << green_min << " green_max=" << green_max
         << " cycle_time=" << cycle_time << "\n";
    cerr << "[ga] starting best delay=" << best_sol.second << "\n";
  }

  // Early stopping: stop if no improvement for N iterations
  const int EARLY_STOP_PATIENCE = 5;
  int no_improvement_count = 0;
  double prev_best = best_sol.second;

  for (int iter = 0; iter < max_iter; ++iter) {
    SelectionInfo sel_info = prepare_selection(population, beta);
    vector<population_element> next_gen(pop_size);

    // Elitism: carry over the best
    next_gen[0] = population[0];

#pragma omp parallel
    {
      mt19937 local_rng(rng() + 100 * (iter + 1));
#ifdef _OPENMP
      local_rng.seed(rng() + 100 * (iter + 1) + 7 * omp_get_thread_num());
#endif

#pragma omp for schedule(static)
      for (int i = 1; i < pop_size; i += 2) {
        int i1 = roulette_wheel_selection(sel_info, local_rng);
        int i2 = roulette_wheel_selection(sel_info, local_rng);

        auto children =
            crossover(population[i1].first, population[i2].first, local_rng);

        vi c1 = mutate(children.first, mutation_rate, green_min, green_max,
                       local_rng);
        normalize_greens(c1, cycle_time, green_min, green_max);
        double d1 = 0;
        for (int j = 0; j < num_lights; j++)
          d1 += fitness_function(cycle_time, c1[j], lcs[j]);
        next_gen[i] = {std::move(c1), d1};

        if (i + 1 < pop_size) {
          vi c2 = mutate(children.second, mutation_rate, green_min, green_max,
                         local_rng);
          normalize_greens(c2, cycle_time, green_min, green_max);
          double d2 = 0;
          for (int j = 0; j < num_lights; j++)
            d2 += fitness_function(cycle_time, c2[j], lcs[j]);
          next_gen[i + 1] = {std::move(c2), d2};
        }
      }
    }

    population = std::move(next_gen);
    sort(population.begin(), population.end(),
         [](const population_element &a, const population_element &b) {
           return a.second < b.second;
         });

    if (population.front().second < best_sol.second) {
      best_sol = population.front();
      no_improvement_count = 0;
      if (verbose) {
        cerr << "[iter " << iter + 1 << "] new best delay = " << best_sol.second
             << "  green = [" << best_sol.first[0] << "," << best_sol.first[1]
             << "," << best_sol.first[2] << "," << best_sol.first[3] << "]\n";
      }
    } else {
      no_improvement_count++; // Increment counter
      if (verbose) {
        cerr << "[iter " << iter + 1 << "] best delay = " << best_sol.second
             << " (no improvement: " << no_improvement_count << "/"
             << EARLY_STOP_PATIENCE << ")\n";
      }
    }
    best_delays.push_back(best_sol.second);

    /*if we already got the answer then there is no point of waiting for better answer in this case sot for all */
    if (no_improvement_count >= EARLY_STOP_PATIENCE) {
      if (verbose) {
        cerr << "[ga] Early stopping at iter " << iter + 1
             << " (no improvement for " << EARLY_STOP_PATIENCE
             << " iterations)\n";
      }
      break;
    }
  }

  return {best_sol, best_delays};
}

int main(int argc, char **argv) {
  if (argc < 5) {
    cerr << "{\"error\":\"Usage: ga_cli north south west east "
            "[--verbose|-v]\"}\n";
    return 1;
  }

  bool verbose = false;
  for (int i = 5; i < argc; ++i) {
    string s = argv[i];
    if (s == "-v" || s == "--verbose")
      verbose = true;
  }

  vi cars(4);
  FOR(i,0,4) {
    try {
      cars[i] = stoi(string(argv[i + 1]));
      if (cars[i] < 0)
        cars[i] = 0;
    } catch (...) {
      cars[i] = 0;
    }
  }

  vector<LightConstants> lcs(4);
   FOR(i,0,4) {
    lcs[i].x = double(20 - cars[i]) / 20.0;
    lcs[i].c = 20.0;
    double rad = (lcs[i].x - 1.0) + (lcs[i].x - 1.0) * (lcs[i].x - 1.0) +
                 ((16.0 * lcs[i].x) / lcs[i].c);
    lcs[i].a2_ri1 = 173.0 * (lcs[i].x * lcs[i].x) * sqrt(max(0.0, rad));
  }

  int pop_size = 400;
  int num_lights = 4;
  int max_iter = 25;
  int green_min = 10;
  int green_max = 60;
  int cycle_time = 160 - 12;
  double mutation_rate = 0.15;
  double beta = 4.0;

  if (verbose) {
    cerr << "Starting with cars = [" << cars[0] << "," << cars[1] << ","
         << cars[2] << "," << cars[3] << "]\n";
  }

  auto res =
      genetic_algorithm(pop_size, num_lights, max_iter, green_min, green_max,
                        cycle_time, mutation_rate, beta, lcs, verbose);
  population_element best = res.first;

  /*Prints logs so can see the mutations*/
  cout << "{\"north\":" << best.first[0] << ",\"south\":" << best.first[1]
       << ",\"west\":" << best.first[2] << ",\"east\":" << best.first[3]
       << ",\"delay\":" << best.second << "}\n";

  if (verbose) {
    // also print a short summary to stderr
    cerr << "GA finished. Final best delay = " << best.second << "\n";
    cerr << "Final greens: N=" << best.first[0] << " S=" << best.first[1]
         << " W=" << best.first[2] << " E=" << best.first[3] << "\n";
  }

  return 0;
}
