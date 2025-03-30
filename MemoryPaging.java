package os;

import java.util.Map;
import java.util.Random;
import java.util.Scanner;
import java.util.TreeMap;

public class MemoryPaging {

	// Simuliramo dinamicko rasporedivanje spremnika
	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		// Korisnik sam odabire ukupnu velicinu spremnika
		System.out.print("Upisite zeljenu ukupnu velicinu spremnika: ");
		int size = sc.nextInt();

		if (size > 100 || size < 1) // Proizvoljno sam odabrala da je maksimalna velicina spremnika 100
			System.err.println("Nemoguce stvoriti spremnik s vise od 100 spremnickih mjesta ili manje od 1 mjesta.");
		else {
			System.out.println();

			char[] tags = new char[size]; // Prikaz indeksa mjesta u spremniku
			char[] memory = new char[size]; // Sadrzaj pojedinog mjesta u spremniku

			int i = 0;
			// Postavljanje inicijalnih vrijednosti spremnika
			for (int j = 0; j < size; ++j) {
				char tag = (char) (i + 48);
				tags[j] = tag;
				memory[j] = '-'; // Slobodno mjesto oznaceno sa '-'

				System.out.print(tag); // Ispis indeksa mjesta u spremniku

				if (i < 9)
					++i;
				else
					i = 0;
			}

			System.out.println();
			// Ispis pocetnih vrijednosti spremnika
			for (char c : memory)
				System.out.print(c); 
			System.out.println();
            
			/* U mapi pamtimo na kojem indeksu pocinje kolika rupa u spremniku, 
			   poredane od najmanje prema najvecoj */
			TreeMap<Integer, Integer> holes = new TreeMap<Integer, Integer>();
			holes.put(0, size); // Na pocetku je cijeli spremnik rupa
			i = 0;
			Random rand = new Random();

			while (true) {
				String action = sc.next(); // Dohvat simbola zeljene akcije
				
                // 'Z' je simbol za zauzimanje prostora
				if (action.equals("Z")) {
					System.out.println();
 
					// Slucajni odabir 1-11 zeljenih mjesta za zauzeti (proizvoljno odabrano da je 11 max)
					int take = rand.nextInt(11) + 1;
					System.out.println("Novi zahtjev " + i + " za zauzimanje " + take + " spremnickih mjesta.");
					System.out.println();
					boolean success = false; // Pamti je li zauzimanje uspjesno

					// Pregledavamo rupe od najmanje do najvece
					for (Map.Entry<Integer, Integer> entry : holes.entrySet()) {
						int index = entry.getKey(); // Pocetak rupe
						int hole = entry.getValue(); // Velicina rupe

						// Zauzmi zeljeni prostor ako u rupi ima dovoljno mjesta
						if (take <= hole) {
							char request = (char) (i + 48);
							for (int j = index; j < take + index; ++j)
								memory[j] = request;

							// U mapu umjesto stare stavi smanjenu rupu ako postoji
							holes.remove(index);
							if (hole != take)
								holes.put(index + take, hole - take);

							success = true;
							break;
						}
					}

					// Ako je prostor uspjesno zauzet ispisi stanje spremnika
					if (success) {
						for (char c : tags)
							System.out.print(c);
						System.out.println();
						for (char c : memory)
							System.out.print(c);
						System.out.println();
					} else // U slucaju neuspjeha ispisi prikladnu poruku
						System.out.println("Nemoguce zazuzeti trazenu memoriju.");

					// Povecaj oznaku zahtjeva
					if (i < 9)
						++i;
					else
						i = 0;
				// 'O' je oznaka za oslobadanje spremnika
				} else if (action.equals("O")) {
					// Korisnik proizvoljno bira zahtjev za oslobadanje
					System.out.println("Koji zahtjev treba osloboditi?");
					int free = sc.nextInt();

					// Oznaka mora biti u rasponu 0-9
					if (free <= 9 && free >= 0) {
						boolean success = false; // Pamti je li oslobadanje uspjesno
						int gap = 0; // Broji broj mjesta novonastale rupe
						int beginIndex = -1; // Pocetak novonastale rupe
						int endIndex = -1; // Kraj novonastale rupe

						// Pretrazujemo zahtjeve po cijelom spremniku
						for (int j = 0; j < size; ++j) {
							char request = (char) (free + 48);
							// Ako je pronaden zeljeni zahtjev oslobodi mjesto
							if (memory[j] == request) {
								memory[j] = '-';
								++gap; // Povecaj broj oslobodenih mjesta
								// Postavi pocetni ineks rupe
								if (beginIndex < 0)
									beginIndex = j;

								// Provjeri jesmo li dosli do kraja jednog bloka zeljenog zahtjeva
								if (memory[j + 1] != request || j == size - 1) {
									endIndex = j; // Postavi indeks kraja rupe

									/* Za postojece rupe provjeravamo postoji li rupa
									   koja zavrsava gdje novonastala pocinje */
									for (Map.Entry<Integer, Integer> entry : holes.entrySet()) {
										int index = entry.getKey();
										int hole = entry.getValue();
										if (index + hole == beginIndex) {
											// Ako postoji pocetni indeks nove rupe je indeks ove rupe
											beginIndex = index; 
											gap += hole; // Povecaj broj mjesta nove rupe
											break;
										}
									}

									/* Za postojece rupe provjeravamo postoji li rupa
									   koja pocinje gdje novonastala zavrsava */									
									for (Map.Entry<Integer, Integer> entry : holes.entrySet()) {
										int index = entry.getKey();
										int hole = entry.getValue();
										if (index == beginIndex + gap) {
											// Ako postoji zavrsni indeks nove rupe je kraj ove rupe
											endIndex = index + hole;
											gap += hole; // Povecaj broj mjesta nove rupe
											holes.remove(index); // Izbrisi staru rupu iz mape
											break;
										}
									}

									// Oznaci da je memorija uspjesno oslobodena
									if (!success)
										success = true;
									// U mapu spremi novu rupu
									holes.put(beginIndex, gap);
									// Za slucaj novog bloka zahtjeva obiljezja rupe se racunaju ispocetka
									gap = 0; 
									beginIndex = -1;
									// Nije potrebno iterirati kroz mjesta za koja smo ustanovili da su prazna
									j = endIndex;
								}
							}
						}

						// U slucaju uspjeha ispisi poruku i stanje spremnika
						if (success) {
							System.out.println("Oslobodio se zahtjev " + free + ".");
							System.out.println();
							for (char c : tags)
								System.out.print(c);
							System.out.println();
							for (char c : memory)
								System.out.print(c);
							System.out.println();
						// U slucaju da je zatrazeno oslobadanje zahtjeva koji nije bio spremljen ispisi prikladnu poruku
						} else 
							System.out.println("Zahtjev " + free + " nije ni bio zauzet.");
					} else // U slusaju krivo zadanog zahtjeva ispisi poruku
						System.out.println("Kriva oznaka zahtjeva, zahtjevi imaju oznaku 0-9.");
				// 'P' sam proizvoljno odabrala kao oznaku za preslagivanje spremnika
				} else if (action.equals("P")) {
					char[] pom = new char[size]; // Pomocno polje
					int k = 0;

					// Sva zauzeta mjesta spremi po redu na lijevu stranu u pomocno polje
					for (char c : memory) 
						if (c != '-') 
							pom[k++] = c;
	
                    // Sva slobodna mjesta na desnu stranu
					for (int j = k; j < size; ++j)
						pom[j] = '-';
					
					memory = pom; // Spremi preslozeno polje
					holes.clear(); // Izbrisi postojece rupe
					// Ako ima slobodnih mjesta spremi jednu veliku rupu s desna
					if (i < size)
						holes.put(k, size - k);

					// Ispisi poruku i stanje spremnika
					System.out.println("Spremnik preslozen.");
					System.out.println();
					for (char c : tags)
						System.out.print(c);
					System.out.println();
					for (char c : memory)
						System.out.print(c);
					System.out.println();
				}

			}
		}

	}

}
