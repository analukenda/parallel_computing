#include <iostream>
#include <pthread.h>
#include <csignal>
#include <sys/wait.h>
#include <unistd.h>

using namespace std;

#define BR_FILOZOFA 5 // Ukupan broj filozofa

char filozof_radi[BR_FILOZOFA]; // Oznaka radnje koju filozof obavlja
int vilica_slobodna[BR_FILOZOFA]; // Ako je vilica slobodna 1, u suprotnom 0
pthread_cond_t red[BR_FILOZOFA]; // Red uvjeta za filozofe
pthread_mutex_t monitor; // Monitor za ulazak u kriticni odsjecak

// Funkcija za ispis trenutnih stanja filozofa
void ispisi_stanje(int indeks)
{
          for (int i = 0; i < BR_FILOZOFA; ++i)
                  printf("%c ", filozof_radi[i]);
          printf("(%d)\n", indeks + 1); // Ispis indeksa filozofa pozivatelja
}

// Funkcija simulira operaciju jedenja
void jesti(int indeks)
{
          pthread_mutex_lock(&monitor); // Ulazak u kriticni odsjecak
          filozof_radi[indeks] = 'o'; // Oznaka da filozof ceka da moze jesti
          while (vilica_slobodna[indeks] == 0 || 
                 vilica_slobodna[(indeks + 1) % 5] == 0)
                  // Cekaj dok se ne oslobode lijeva i desna vilica
                  pthread_cond_wait(&red[indeks], &monitor);
          vilica_slobodna[indeks] = 0; // Oznaci da je lijeva vilica zauzeta
          vilica_slobodna[(indeks + 1) % 5] = 0; // Desna vilica zauzeta
          filozof_radi[indeks] = 'X'; // Oznaka da filozof jede
          ispisi_stanje(indeks); // Ispisi trenutno stanje
          pthread_mutex_unlock(&monitor); // Izlazak iz kriticnog odsjecka
    
          sleep(2); // Simulira jedenje

          pthread_mutex_lock(&monitor); // Ulazak u kriticni odsjecak
          // Oznaka da filozof vise ne jede i nastavlja misliti
          filozof_radi[indeks] = 'O'; 
          vilica_slobodna[indeks] = 1; // Lijeva vilica slobodna
          vilica_slobodna[(indeks + 1) % 5] = 1; // Desna vilica slobodna
          // Ako je lijevi filozof cekao vilicu, oslobodi ga iz reda uvjeta
          pthread_cond_signal(&red[(indeks - 1) % 5]);
          // Ako je desni filozof cekao vilicu, oslobodi ga iz reda uvjeta
          pthread_cond_signal(&red[(indeks + 1) % 5]);
          ispisi_stanje(indeks); // Ispisi trenutno stanje
          pthread_mutex_unlock(&monitor); // Izlazak iz kriticnog odsjecka
}

// Posao koji filozof obavlja beskonacno
void *filozof(void *arg)
{
          int *i = (int *)arg; // Indeks filozofa
          while (true) {
                  sleep(3); // Simulira razmisljanje
                  jesti(*i); // Filozof krece jesti
           }
}

int main(void)
{
          // Zasebna struktura podataka za svaku dretvu
          pthread_t dretve[BR_FILOZOFA]; 
          for (int i = 0; i < BR_FILOZOFA; ++i) {
                  filozof_radi[i] = 'O'; // Svaki filozof na pocetku misli
                  vilica_slobodna[i] = 1; // Svaka vilica je u startu slobodna
                  // Inicijaliziraj red cekanja
                  pthread_cond_init(&red[i], NULL); 
          }
          pthread_mutex_init(&monitor, NULL); // Inicijaliziraj monitor
          
          // Posebna struktura za argumente pocetne rutine dretve
          int *BR = new int[BR_FILOZOFA];
          
          // Stvori potreban broj dretvi filozofa
          for (int i = 0; i < BR_FILOZOFA; ++i) {
                  *(BR + i) = i; // Indeks dretve
                int unsuccess = pthread_create(&dretve[i], NULL,
                                               filozof, (void *)(BR + i));

                // Ako dretva nije uspjesno stvorena prekini program
                if (unsuccess) {
                        printf("Ne mogu stvoriti novog filozofa.\n");
                        exit(1);
                }
           }
    
          // Pricekaj da sve dretve zavrse
          for (int i = 0; i < BR_FILOZOFA; ++i)
                  pthread_join(dretve[i], NULL);

          pthread_mutex_destroy(&monitor); // Obrisi monitor
          // Obrisi red uvjeta
          for (int i = 0; i < BR_FILOZOFA; ++i)
                  pthread_cond_destroy(&red[i]);                  

          return 0;
}