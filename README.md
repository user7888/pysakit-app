# **Kuvaus**
Sovellus, jonka avulla käyttäjä voi
seurata joukkoliikenteen
pysäkkien aikatauluja.

## **Projektin tilanne**

Sovelluksen ominaisuudet
- Päänäkymä, jossa näytetään käyttäjän valitsemat pysäkit. Käyttäjälle
  näytetään myös seurattujen pysäkkien ja reittien määrä.
- Uuden pysäkin lisääminen pysäkin tunnuksella.
- Hakutoiminto pysäkkien etsimiseen. Pysäkkejä voi hakea pysäkin
  nimen ja kadunnimen perusteella.
- Käyttäjä voi poistaa pysäkin seurannasta.
- Yksittäisen pysäkin näkymä, jossa näkyy pysäkille saapuvat 
  joukkoliikennevälineet.
- Kirjautuminen ja käyttäjätunnuksen rekisteröinti.

## **Käynnistämisohjeet**

Sovellus ei ole testattavissa Fly.io:ssa. Alla ohjeet paikalliseen
testaamiseen.

**HUOM:** Toimiakseen sovellus tarvitsee verkkoyhteyden.

**1. Kloonaa repositorio**
```
$ git clone https://github.com/user7888/pysakit-app.git
```
**2. Aktivoi virtuaaliympäristö ja asenna riippuvuudet**
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r ./requirements.txt
```

**3. Määritä tietokannan skeema**
```
$ psql < schema.sql
```
**4. Määritä ympäristömuuttujat**

Luo tiedosto **.env** ja lisää sinne muuttujat:
```
DATABASE_URL=<tietokannan-paikallinen-osoite>
SECRET_KEY=<salainen-avain>
```

**5. Käynnistä sovellus**
```
$ flask run
```

**Sovelluksen suunnitellut ominaisuudet**
- Kotinäkymä, josta käyttäjä näkee valitsemansa joukkoliikenteen pysäkit.
- Käyttäjä voi lisätä ja poistaa pysäkkejä kotinäkymästä.
- Valitsemalla pysäkin käyttäjälle avautuu tarkempi näkymä, josta näkyy saapuvien 
  bussien tai raitiovaunujen aikataulut. Käyttäjälle voidaan näyttää myös tietoa 
  häiriöstä tai viivästyksistä.
- Hakutoiminto, jonka avulla käyttäjä voi etsiä haluamansa pysäkit. Tarkempi     toteutus
  vielä epävarma, haku voisi toimia esimerkiksi pysäkin
  nimen tai koodin perusteella. Myös sijainnin tai linjan perusteella toimiva
  haku voisi olla mahdollinen.
- Käyttäjä voi antaa pysäkeille haluamansa lempinimen.
- Käyttäjä voi kirjautua sisään ja ulos sekä
  luoda uuden tunnuksen.




