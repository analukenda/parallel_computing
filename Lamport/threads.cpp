#include <iostream>
#include <pthread.h>
#include <cstdlib>
#include <sys/wait.h>

using namespace std;

int N; // Broj dretvi koje treba stvoriti
int M; // Broj koraka petlje koje svaka dretva treba obaviti
int A = 0; // Globalna varijabla postavljena na 0

// Posao koji svaka dretva treba obaviti
void *dretva(void *arg)
{
          // Zadani broj ponavljanja uvecavaj varijablu A za 1
          for (int i = 0; i < M; ++i)
                  ++A; 
}

int main(int argc, char *argv[])
{
          N = atoi(argv[1]); // Prvi argument terminala je broj dretvi
          M = atoi(argv[2]); // Drugi argument terminala je broj ponavljanja

          pthread_t dretve[N]; // Zasebna struktura podataka za svaku dretvu
          
          // Stvori zadani broj dretvi
          for (int i = 0; i < N; ++i) {
                  int unsuccess = pthread_create(&dretve[i], NULL, dretva, NULL);
                  // Ako dretva nije uspjesno stvorena prekini program
                  if (unsuccess) {
                          printf("Ne mogu stvoriti novu dretvu.\n");
                          exit(1);
                   }
          }     
          
          // Pricekaj da sve dretve zavrse
          for (int i = 0; i < N; ++i) {
                  pthread_join(dretve[i], NULL); 
          }
          
          printf("A=%d\n",A); // Ispis globalne varijable
          
          return 0;
}