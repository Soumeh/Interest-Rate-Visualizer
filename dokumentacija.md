# Dokumentacija ETL_proj

## Uvod / Opšti opis

ETL_proj je aplikacija za ekstrakciju, transformaciju i učitavanje (ETL) finansijskih podataka sa sajta Narodne banke Srbije (NBS). Aplikacija preuzima Excel fajlove sa podacima o kreditima, depozitima i kamatnim stopama, obrađuje ih i skladišti u PostgreSQL bazi podataka. Podaci se zatim prikazuju korisnicima kroz interaktivni dashboard koji omogućava vizuelizaciju i analizu finansijskih trendova.

Aplikacija je dizajnirana da bude modularna, skalabilna i laka za održavanje. Koristi moderne tehnologije kao što su Python, Flask, Dash, SQLAlchemy i Docker za razvoj, implementaciju i održavanje.

## Arhitektura sistema

Sistem je organizovan u nekoliko ključnih komponenti:

### src/db - Baza podataka
Sadrži sve klase za obradu baza podataka. Ova komponenta definiše modele podataka i pruža metode za interakciju sa bazom podataka. Glavni elementi uključuju:
- `SerializableTable` - Osnovna klasa koja pruža funkcionalnosti za serijalizaciju i deserijalizaciju podataka
- Specifične tabele za različite vrste finansijskih podataka:
  - `household` - Podaci o kreditima i depozitima domaćinstava
  - `non_financial` - Podaci o kreditima i depozitima nefinansijskog sektora
  - `total` - Ukupni podaci o kreditima i depozitima

### src/etl - Ekstrakcija, transformacija i učitavanje podataka
Sadrži kod za skidanje i ažuriranje podataka sa Excel fajlova na bazu podataka. Ova komponenta:
- Preuzima Excel fajlove sa sajta NBS
- Kešira fajlove lokalno radi efikasnosti
- Obrađuje podatke i priprema ih za skladištenje
- Učitava obrađene podatke u PostgreSQL bazu podataka

### src/backend - Serverski kod
Sadrži sav serverski kod koji treba da bude pristupačan korisniku. Implementiran je kao Flask aplikacija koja:
- Konfiguriše vezu sa bazom podataka
- Integriše se sa Dash frontend aplikacijom
- Pruža API za pristup podacima

### src/frontend - Dashboard
Sadrži kod za sklapanje dashboarda. Implementiran je koristeći Dash framework koji omogućava:
- Interaktivne vizuelizacije podataka
- Filtriranje podataka po različitim kriterijumima (godina, mesec, tip podataka)
- Eksportovanje podataka u CSV format
- Prilagodljiv interfejs sa opcijom za promenu teme

### src/common - Zajedničke komponente
Sadrži zajedničke funkcije, konstante i pomoćne klase koje se koriste u različitim delovima aplikacije.

## Funkcionalnosti

Aplikacija pruža sledeće ključne funkcionalnosti:

### ETL proces
- Automatsko preuzimanje Excel fajlova sa sajta NBS
- Parsiranje i validacija podataka
- Transformacija podataka u odgovarajući format
- Učitavanje podataka u PostgreSQL bazu podataka

### Vizuelizacija podataka
- Grafički prikaz finansijskih podataka kroz vreme
- Filtriranje podataka po godini, mesecu i tipu podataka
- Prilagodljivi grafikoni koji se ažuriraju u realnom vremenu

### Analiza podataka
- Tabelarni prikaz detaljnih podataka
- Mogućnost eksportovanja podataka u CSV format za dalju analizu
- Uporedni pregled različitih kategorija finansijskih podataka

### Korisnički interfejs
- Intuitivni dashboard sa padajućim menijima za selekciju podataka
- Opcija za promenu teme (svetla/tamna)
- Responzivni dizajn prilagođen različitim uređajima

## Održavanje i razvoj

### Zahtevi
Za razvoj i pokretanje aplikacije potrebno je:
- Python 3.12
- PostgreSQL 17
- Docker i Docker BuildKit
- UV (alat za upravljanje Python paketima)

### Razvoj
Za razvoj aplikacije:
1. Instalirajte potrebne pakete koristeći UV:
   ```bash
   uv sync
   ```

2. Formatirajte kod koristeći Ruff:
   ```bash
   ruff format
   ruff check --fix
   ```

### Pokretanje aplikacije
Aplikacija se može pokrenuti na dva načina:

1. Lokalno:
   - Podesite .env fajl sa odgovarajućim vrednostima za bazu podataka
   - Pokrenite ETL proces: `python -m src.etl`
   - Pokrenite backend server: `python -m src.backend`

2. Koristeći Docker:
   - Pokrenite aplikaciju koristeći Docker Compose:
     ```bash
     docker-compose up
     ```

### Dodavanje novih funkcionalnosti
Za dodavanje novih funkcionalnosti:
1. Dodajte nove modele u src/db direktorijum
2. Ažurirajte ETL proces u src/etl/__main__.py
3. Dodajte nove komponente u frontend aplikaciju u src/frontend/app.py
4. Testirajte promene lokalno pre implementacije

### Održavanje
Za održavanje aplikacije:
1. Redovno ažurirajte zavisnosti
2. Pratite logove za potencijalne greške
3. Periodično proveravajte da li su URL-ovi za preuzimanje Excel fajlova i dalje validni
4. Optimizujte upite baze podataka po potrebi

## Tehnicki zahtevi
- Frontend tehnologije - Uradjene koristieci Plotly Express.
- Backend tehnologije - Uradjene koristeci Flask.
- Baza podataka - Uradjena koristeci PostgreSQL.
- Integracija sa izvorima podataka i ažuriranje - Podaci se azuriraju dnevno.
- Sigurnosni zahtevi - Banka moze da dozvoli pristup samo na lokalnoj mrezi.
- Performanse i skalabilnost - Kesiranje jos ne postoji ali je aplikacija svakako poprilicno brza.
- Kompatibilnost i okruženje - Kod jos uvek nije pravilno dokumentisan, postoji docker container za lak deployment. 

## Funkcionalni Zahtevi
- Institucionalni sektor korisnika kredita/depozita - Trenutno su dostupni samo prikazi za privredu i stanovništvo, ne ukupno.
- Veličina preduzeća (za pravna lica) - 