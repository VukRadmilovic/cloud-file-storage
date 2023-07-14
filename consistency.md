# Problem konzistencije u sistemu sa S3 i DynamoDB skladištima

## Problem
U okviru našeg sistema, koristimo Amazon S3 za čuvanje sadržaja, dok su dodatne informacije o tom sadržaju čuvane u Amazon DynamoDB tabeli. Međutim, suočili smo se sa problemom konzistencije između ova dva skladišta. Kada korisnik izvrši dodavanje ili izmenu sadržaja, postoji mogućnost da se dođe do nekonzistentnog stanja između S3 i DynamoDB skladišta. Predstavićemo naš pristup rešavanju ovog problema i objasniti kako sistem garantuje konzistentnost uprkos eventualnim prekidima internet konekcije ili neuspešnim HTTP zahtevima.

## Rešenje
1. Dodavanje sadržaja:
Kada korisnik želi da dodaje sadržaj u sistem, prvo šalje HTTP zahtev ka našoj Lambda funkciji. Lambda funkcija obrađuje ovaj zahtev tako što upisuje metapodatke u DynamoDB tabelu i postavlja odgovarajući flag (`valid`) na `false` za taj unos. Nakon toga, Lambda funkcija generiše S3 pre-signed URL za postupak otpremanja (upload) fajla. Ovaj URL se vraća korisniku putem HTTP odgovora. Kada korisnik otpremi fajl na dobijeni S3 pre-signed URL, Lambda funkcija koja je povezana sa S3 okidačem (trigger) se aktivira. Ako je uspešno otpremljen fajl, menja se vrednost flaga `valid` na `true` za odgovarajući unos u DynamoDB tabeli. Na ovaj način, garantujemo da se samo uspešno otpremljeni sadržaj označava kao validan i samo taj sadržaj se vraća korisniku kada se listaju podaci.

2. Izmena sadržaja:
Kada korisnik želi da izmeni dodatne informacije o određenom sadržaju, prvo pravimo duplikat unosa u DynamoDB tabeli koji sadrži nove informacije. Zatim, koristimo isti proces kao kod dodavanja sadržaja: generišemo S3 pre-signed URL za postupak izmene (upload) fajla, korisnik otprema fajl na taj URL, a Lambda funkcija okidač pri uspešnom otpremanju menja originalni unos u DynamoDB tabeli sa novim informacijama samo ako je izmena uspešno završena.

3. Brisanje sadržaja:
Kada korisnik želi da obriše određeni sadržaj, šalje jedan HTTP zahtev. Nema dodatnih koraka u ovom procesu jer je samo jedan zahtev dovoljan da se izvrši brisanje iz obe S3 i DynamoDB skladišta. Ovo je jednostavniji slučaj jer nema potrebe za sinhronizacijom između dveju baza.

## Zaključak
Konzistentnost između S3 i DynamoDB skladišta je od ključne važnosti kako bi naš sistem pravilno funkcionisao. Implementirali smo rešenje koje se fokusira na serversku stranu i garantuje konzistentnost uprkos eventualnim prekidima internet konekcije ili neuspešnim HTTP zahtevima. Naše rešenje uključuje upisivanje metapodataka i korišćenje flaga `valid` u DynamoDB tabeli, kao i korišćenje Lambda funkcija za validaciju i izmene unosa. Na klijentskoj strani, korisnik dobija S3 pre-signed URL koji omogućava bezbedno otpremanje sadržaja. Ovim pristupom obezbeđujemo da samo uspešno otpremljeni sadržaj bude označen kao validan i da se izmene primene samo ako su uspešno završene. Na taj način, rešavamo problem konzistencije i pružamo pouzdano iskustvo korisnicima našeg sistema.
