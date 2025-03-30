#include <iostream>
#include <unistd.h>
#include <sys/shm.h>
#include <cstdlib>
#include <sys/wait.h>

using namespace std;

int N; // Broj procesa koje treba stvoriti
int M; // Broj koraka u petlji koje svaki proces treba proci
int *A; // Zajednicka varijabla
int ID_SEGMENTA; // Id segmenta zajednickog spremnika

// Posao koji svaki proces treba obaviti
void proces()
{         
          // Zadani broj ponavljanja uvecavaj varijablu A za 1
          for (int i = 0; i < M; ++i)
                  *A += 1; 
}

int main(int argc, char *argv[])
{
          N = atoi(argv[1]); // Prvi argument terminala je broj procesa
          M = atoi(argv[2]); // Drugi argument terminala je broj ponavljanja
          ID_SEGMENTA = shmget(IPC_PRIVATE, sizeof(int), 0600); /* Zauzimanje
                                                                   memorije */
          
          // Prekid programa zbog nemogucnosti zauzimanja zajednicke memorije
          if (ID_SEGMENTA == -1) {
                  printf("Ne mogu zauzeti zajednicku memoriju.\n");
                  exit(1);
          }

          A = (int *)shmat(ID_SEGMENTA, NULL, 0); // A spremi u segment
          *A = 0; // Postavi zajednicku varijablu na 0

          for (int i = 0; i < N; ++i) {
                  int success = fork(); // Stvori N procesa
                  // Ako je uspjesno stvoren zadaj rad i na kraju ga zaustavi
                  if (success == 0) {
                          proces();
                          exit(0);
                  // Ako nije uspjesno stvoren zaustavi program
                  } else if (success == -1) {
                          printf("Ne mogu stvoriti novi proces.\n");
                          exit(1);
                  }
          }
          
          // Pricekaj da svi procesi zavrse
          for (int i = 0; i < N; ++i)
                  wait(NULL); 
                   
          printf("A=%d\n", *A); // Ispis zajednicke varijable
          
          shmdt((int *)A); // Odvoji segment
          shmctl(ID_SEGMENTA, IPC_RMID, NULL); // Izbrisi segment
          
          return 0;
}
