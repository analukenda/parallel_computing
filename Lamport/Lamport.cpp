#include <iostream>
#include <pthread.h>
#include <atomic>
#include <sys/wait.h>
#include <stdlib.h>

using namespace std;

int N; // Broj dretvi koje treba stvoriti
int M; // Broj koraka petlje koje svaka dretva treba obaviti
atomic<int> *A = new atomic<int>; // Globalna varijabla
atomic<int> *BROJ; // Brojevi dodijeljeni dretvama, 0 kad dretva ne trazi ulaz
atomic<int> *ULAZ; // 1 ako se dretvi dodjeljuje broj, 0 u suprotnom
int MAX_BROJ = 0; // Trenutno najveci dodijeljeni broj

// Ulazak u kriticni odsjecak
void udi_u_kriticni_odsjecak(int i)
{
          *(ULAZ + i) = 1; // Naznaci da se dretvi dodjeljuje broj

          // Pronadi najveci dodijeljeni broj
          for (int j = 0; j < N; ++j) 
                  if (*(BROJ + j) > MAX_BROJ)
                          MAX_BROJ = *(BROJ + j);
    
          *(BROJ + i) = MAX_BROJ + 1; // Dretvi daj broj za 1 veci od najveceg
          *(ULAZ + i) = 0; // Kraj dodjele broja
    
          // Provjera ostalih dretvi
          for (int j = 0; j < N; ++j) {
                  // Pricekaj ako dretva ceka dodjelu broja
                  while (*(ULAZ + j) != 0); 
                  /* Pricekaj ako dretva na cekanju ima manji broj ili 
                  jednaki broj ali manji indeks */
                  while (*(BROJ + j) != 0 && (*(BROJ + j) < *(BROJ + i) || 
                         (*(BROJ + j) == *(BROJ + i) && j < i)));
          }
}

// Izlazak iz kriticnog odsjecka
void izadi_iz_kriticnog_odsjecka(int i)
{
          *(BROJ + i) = 0; // Dretva vise ne ceka na ulaz
}

// Posao koji svaka dretva treba obaviti
void *dretva(void *arg)
{
          int *i = (int *)arg; // Indeks dretve
    
          // Zadani broj ponavljanja povecaj A za 1
          for (int j = 0; j < M; ++j) {
                  // Ulaz u KO prije koristenja zajednicke varijable
                  udi_u_kriticni_odsjecak(*i); 
                  *(A) = *(A) + 1;
                  // Izlaz iz KO poslije koristenja zajednicke varijable
                  izadi_iz_kriticnog_odsjecka(*i); 
          }
}

int main(int argc, char *argv[])
{
          N = atoi(argv[1]); // Prvi argument terminala je broj dretvi
          M = atoi(argv[2]); // Drugi argument terminala je broj ponavljanja
    
          *A = 0; // Globalnu varijablu postavlja na 0
          pthread_t *dretve; // Zasebna struktura podataka za svaku dretvu
    
          // Zauzimanje memorije
          atomic<int> *mem = (atomic<int> *)malloc(sizeof(int) * (N + N) 
                              + N * sizeof(pthread_t));
          ULAZ = mem;
          BROJ = ULAZ + N;
          dretve = (pthread_t *)(BROJ + N);
    
          // Inicijalizacija varijabli ULAZ i BROJ
          for (int i = 0; i < N; ++i) {
                  *(ULAZ + i) = 0;
                  *(BROJ + i) = 0;
          }

          // Posebna struktura za argumente pocetne rutine dretve
          int *BR = new int[N]; 
    
          // Stvori zadani broj dretvi
          for (int i = 0; i < N; ++i) {
                  *(BR + i) = i; // Indeks dretve
                  int unsuccess = pthread_create(dretve + i, NULL, 
                                                 dretva, (void *)(BR + i));

                  // Ako dretva nije uspjesno stvorena prekini program
                  if (unsuccess) {
                          printf("Ne mogu stvoriti novu dretvu.\n");
                          exit(1);
                  }
          }
          // Pricekaj da sve dretve zavrse
          for (int i = 0; i < N; ++i)
                  pthread_join(*(dretve + i), NULL);
        
          cout << ("A=") << *A << endl; // Ispis globalne varijable
      
          return 0;
}
