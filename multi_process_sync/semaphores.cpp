#include <iostream>
#include <cstdlib>
#include <unistd.h>
#include <sys/shm.h>
#include <ctime>
#include <semaphore.h>
#include <csignal>

using namespace std;

#define BR_SOBOVA 10 // Ukupan broj sobova

int *spremni_sobovi; // Broj sobova pred kucom
int *gladni_sobovi; // Broj sobova koji cekaju hranjenje
int *patuljci_u_problemu; // Broj patuljaka koji cekaju konzultacije
sem_t *KO; // Semafor koji stiti zajednicke varijable
sem_t *budenje; // Semafor signalizira budenje Djeda Bozicnjaka
sem_t *sob_se_vratio; // Semafor signalizira povratak soba
sem_t *konzultacije; // Semafor signalizira konzultacije s patuljcima

// Posao koji Djed Bozicnjak obavlja beskonacno
void djed_bozicnjak()
{
          while (true) {
                  sem_wait(budenje); // Cekaj signal za budenje
                  printf("Djed Bozicnjak se probudio.\n");
                  
                  /* Ako su svi sobovi stigli i ima patuljaka pred kucom
                  Djed Bozicnjak raznosi darove */
                  if (*spremni_sobovi == BR_SOBOVA && *patuljci_u_problemu > 0) {
                          printf("Svi sobovi su pred vratima. ");
                          printf("Patuljci mogu pricekati. ");
                          printf("Vrijeme je za poklone!\n");
                          sleep(2); // Simuliran raznos darova
                          printf("Pokloni razneseni. ");
                          
                          sem_wait(KO); // Ulazak u KO
                          // Posalji sobove na godisnji
                          for (int i = 0; i < BR_SOBOVA; ++i)
                                  sem_post(sob_se_vratio);
                          *gladni_sobovi = 0;
                          *spremni_sobovi = 0; 
                          printf("Sobovi idu na godisnji.\n");
                          sem_post(KO); // Izlazak iz kriticnog odsjecka
                  }
                  
                  // Ako su gladni svi sobovi i nema patuljaka, nahrani sobove
                  if (*gladni_sobovi == BR_SOBOVA) {
                          printf("Hranim sobove.\n");
                          sleep(2); // Simulirano hranjenje
                          sem_wait(KO); // Ulazak u kriticni odsjecak
                          *gladni_sobovi = 0; // Nema vise gladnih sobova
                          printf("Sobovi nahranjeni.\n");
                          sem_post(KO); // Izlazak iz kriticnog odsjecka
                          }
                 
                 /* Dok pred vratima ceka 3 ili vise patuljaka, 
                 primaj ih na konzultacije */
                  while (*patuljci_u_problemu > 2) {
                          printf("Konzultacije pocele.\n");
                          sleep(2); // Simulacija konzultacija
                          printf("Konzultacije zavrsile.\n");
                          sem_wait(KO); // Ulazak u kriticni odsjecak
                          // Otpusti patuljke iz reda cekanja
                          for (int i = 0; i < 3; ++i)
                                  sem_post(konzultacije); 
                          *patuljci_u_problemu -= 3;
                          sem_post(KO); // Izlazak iz kriticnog odsjecka
                  }
                  
                  // Djed Bozicnjak moze nazad na spavanje
                  printf("Djed Bozicnjak ide nazad na spavanje.\n");
          }
}

// Novi sob povratnik s godisnjeg odmora
void sob()
{
          sem_wait(KO); // Ulazak u kriticni odsjecak
          printf("%d. sob se vratio s godisnjeg odmora.\n", ++*spremni_sobovi);
          ++*gladni_sobovi; // Jedan sob vise ceka na hranjenje
          if (*spremni_sobovi == BR_SOBOVA) {
                  printf("Svi sobovi su se vratili. ");
                  /* Ako su se svi sobovi vratili, treba 
                  poslati signal za budenje Djeda Bozicnjaka */
                  printf("Treba probuditi Djeda Bozicnjaka.\n");
                  sem_post(budenje);
          }
          sem_post(KO); // Izlazak iz kriticnog odsjecka
          sem_wait(sob_se_vratio); // Dodaj soba u red sobova povratnika
}

// Novi patuljak ceka na konzultacije
void patuljak()
{
          sem_wait(KO); // Ulazak u kriticni odjsecak
          printf("%d. patuljak ceka konzultacije.\n", ++*patuljci_u_problemu);
          /* Ako 3 patuljka cekaju, treba poslati
          signal za budenje Djeda Bozicnjaka */
          if (*patuljci_u_problemu == 3) {
                  printf("Tri patuljka cekaju na konzultacije. ");
                  printf("Treba probuditi Djeda Bozicnjaka.\n");
                  sem_post(budenje);
          }
          sem_post(KO); // Izlazak iz kriticnog odsjecka
          sem_wait(konzultacije); // Dodaj patuljka u red za konzultacije
}

// Oslobadanje memorije pri prekidu programa
void kraj(int id)
{
              sem_destroy(KO);
              sem_destroy(budenje);
              sem_destroy(sob_se_vratio);
              sem_destroy(konzultacije);
              shmdt(KO);
              exit(0);
}

int main(void)
{
          // Rezerviranje memorije
          int ID_SEGMENTA = shmget(IPC_PRIVATE, 
                                   4 * sizeof(sem_t) + 3 * sizeof(int), 0600);
          KO = (sem_t *)shmat(ID_SEGMENTA, NULL, 0);
          shmctl(ID_SEGMENTA, IPC_RMID, NULL);
          
          budenje = KO + 1;
          sob_se_vratio = budenje + 1;
          konzultacije = sob_se_vratio + 1;

          spremni_sobovi = (int *)(konzultacije + 1);
          gladni_sobovi = (int *)(spremni_sobovi + 1);
          patuljci_u_problemu = (int *)(gladni_sobovi + 1);
          
          *gladni_sobovi = 0;
          *spremni_sobovi = 0;
          *patuljci_u_problemu = 0;
          
          // Semafor za KO prolazan, razliciti procesi
          sem_init(KO, 1, 1); 
          // Semafor za budenje neprolazan, razliciti procesi
          sem_init(budenje, 1, 0);
          // Semafor za sobove povratnike neprolazan, razliciti procesi 
          sem_init(sob_se_vratio, 1, 0); 
          // Semafor za konzultacije neprolazan, razliciti procesi 
          sem_init(konzultacije, 1, 0);
          
          // Na signal SIGINT oslobodi memoriju i prekini program
          sigset(SIGINT, kraj); 
    
          int success = fork();
          // Stvori proces Djeda Bozicnjaka, ispisi poruku u slucaju neuspjeha 
          if (success == 0) {
                  djed_bozicnjak();
                  exit(0);
          } else if (success == -1) {
                  printf("Nemoguce stvoriti dretvu Djeda Bozicnjaka.\n");
                  exit(1);
          }
          
          printf("Svi sobovi su na godisnjem odmoru.\n");
          printf("Nema patuljaka s problemom.\n");
          printf("Djed Bozicnjak spava.\n");
    
          srand((unsigned)time(0));
          while (true) {
                  sleep(rand() % 1 + 3); // Kratka pauza
                  
                  /* Ako svi sobovi nisu stigli i ako je
                  sansa za dolazak soba > 50% stvori proces soba */
                  if (*spremni_sobovi < BR_SOBOVA ) {
                          if (rand() % 1 + 10 > 5) {
                                  success = fork();
                                  if (success == 0) {
                                          sob();
                                          exit(0);
                                   // Ispisi poruku u slucaju neuspjeha
                                   } else if (success == -1) {
                                          printf("Ne mogu stvoriti soba.\n");
                                          exit(1);
                                  }
                          }
                  }
                  
                  /* Ako je sansa za dolazak patuljka > 50% 
                  stvori proces patuljka */
                  if (rand() % 1 + 10 > 5) {
                          success = fork();
                          if (success == 0) {
                                  patuljak();
                                  exit(0);
                          }
                          // Ispisi poruku u slucaju neuspjeha
                          else if (success == -1) {
                                  printf("Nemoguce stvoriti patuljka.\n");
                                  exit(1);
                          }
                   }
          }

          return 0;
}