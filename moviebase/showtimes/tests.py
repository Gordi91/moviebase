from pytz import timezone
from random import randint, sample

from django.test import TestCase
from faker import Faker
from rest_framework.test import APITestCase

from movielist.models import Person, Movie
from showtimes.models import Cinema, Screening


class CinemaTestCase(APITestCase):
    ID = 0

    def setUp(self):
        """Populte test database with random data."""
        self.faker = Faker("pl_PL")
        for _ in range(5):
            Person.objects.create(name=self.faker.name())
        for _ in range(3):
            self._create_fake_movie()
        for _ in range(3):
            self._create_fake_cinema()
        for _ in range(5):
            self._create_fake_screening()

    def _random_person(self):
        """Return a random Person object from db."""
        people = Person.objects.all()
        return people[randint(0, len(people) - 1)]

    def _find_person_by_name(self, name):
        """Return the first `Person` object that matches `name`."""
        return Person.objects.filter(name=name).first()

    def _fake_movie_data(self):
        """Generate a dict of movie data

        The format is compatible with serializers (`Person` relations
        represented by names).
        """
        movie_data = {
            "title": "{} {}".format(self.faker.job(), self.faker.first_name()),
            "description": self.faker.sentence(),
            "year": int(self.faker.year()),
            "director": self._random_person().name,
        }
        people = Person.objects.all()
        actors = sample(list(people), randint(1, len(people)))
        actor_names = [a.name for a in actors]
        movie_data["actors"] = actor_names
        # print(movie_data["title"])
        return movie_data

    def _create_fake_movie(self):
        """Generate new fake movie and save to database."""
        movie_data = self._fake_movie_data()
        movie_data["director"] = self._find_person_by_name(movie_data["director"])
        actors = movie_data["actors"]
        del movie_data["actors"]
        new_movie = Movie.objects.create(**movie_data)
        for actor in actors:
            new_movie.actors.add(self._find_person_by_name(actor))

    def _find_movie_by_title(self, title):
        """Return the first `Movie` object that matches `title`."""
        return Movie.objects.filter(title=title).first()

    def _find_cinema_by_name(self, name):
        """Return the first 'Cinema' object that matches 'name'."""
        return Cinema.objects.filter(name=name).first()

    def _fake_cinema_data(self):
        """Generate a dict of movie data"""

        cinema_data = {
            "name": self.faker.company(),
            "city": self.faker.city(),
        }
        return cinema_data

    def _create_fake_cinema(self):
        """Generate new fake cinema and save to database"""

        cinema_data = self._fake_cinema_data()
        Cinema.objects.create(**cinema_data)

    def _fake_screening_data(self):
        """Generate fake screening data"""
        screening_data = {
            "movie": self._random_movie().title,
            "cinema": self._random_cinema().name,
            "date": self.faker.date_time_between(start_date="now", end_date="+1y", tzinfo=timezone('Europe/Warsaw')),
        }
        return screening_data

    def _create_fake_screening(self):
        """Generate new fake screening"""

        screening_data = self._fake_screening_data()
        screening_data["movie"] = self._find_movie_by_title(screening_data["movie"])
        screening_data["cinema"] = self._find_cinema_by_name(screening_data["cinema"])
        Screening.objects.create(**screening_data)

    def _random_movie(self):
        """Return a random movie object from db."""
        movies = Movie.objects.all()
        return movies[randint(0, len(movies) - 1)]

    def _random_cinema(self):
        """Return a random cinema object from db."""
        cinemas = Cinema.objects.all()
        return cinemas[randint(0, len(cinemas) - 1)]

    def test_post_cinema(self):
        cinemas_before = Cinema.objects.count()
        new_cinema = self._fake_cinema_data()
        response = self.client.post("/cinemas/", new_cinema, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Cinema.objects.count(), cinemas_before + 1)
        for key, val in new_cinema.items():
            self.assertIn(key, response.data)
            if isinstance(val, list):
                self.assertCountEqual(response.data[key], val)
            else:
                self.assertEqual(response.data[key], val)

    def test_get_cinema_list(self):
        response = self.client.get("/cinemas/", {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cinema.objects.count(), len(response.data))

    def test_get_cinema_detail(self):
        idx = Cinema.objects.all().first().id
        response = self.client.get("/cinemas/{}/".format(idx), {}, format='json')
        self.assertEqual(response.status_code, 200)
        for field in ["name", "city", "movies"]:
            self.assertIn(field, response.data)

    def test_delete_cinema(self):
        response = self.client.delete("/cinemas/1/", {}, format='json')
        self.assertEqual(response.status_code, 204)
        cinema_ids = [cinema.id for cinema in Cinema.objects.all()]
        self.assertNotIn(1, cinema_ids)

    def test_update_cinema(self):
        idx = Cinema.objects.all().first().id
        response = self.client.get("/cinemas/{}/".format(idx), {}, format='json')
        cinema_data = response.data
        new_name = 'Helios'
        cinema_data['name'] = new_name
        new_city = 'Wrocław'
        cinema_data['city'] = new_city
        response = self.client.patch("/cinemas/{}/".format(idx), cinema_data, format='json')
        self.assertEqual(response.status_code, 200)
        cinema_obj = Cinema.objects.get(id=idx)
        self.assertEqual(cinema_obj.name, new_name)
        self.assertEqual(cinema_obj.city, new_city)

    def test_post_screening(self):
        screenings_before = Screening.objects.count()
        new_screening = self._fake_screening_data()
        new_screening['date'] = str(new_screening['date'])
        response = self.client.post("/screenings/", new_screening, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Screening.objects.count(), screenings_before + 1)
        # for key, val in new_screening.items():
        #     self.assertIn(key, response.data)
        #     if isinstance(val, list):
        #         self.assertCountEqual(response.data[key], val)
        #     else:
        #         self.assertEqual(response.data[key], val)

    def test_get_screening_list(self):
        response = self.client.get("/screenings/", {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Screening.objects.count(), len(response.data))

    def test_get_screening_detail(self):
        idx = Screening.objects.all().first().id
        response = self.client.get("/screenings/{}/".format(idx), {}, format='json')
        self.assertEqual(response.status_code, 200)
        for field in ["movie", "cinema", "date"]:
            self.assertIn(field, response.data)

    def test_delete_screening(self):
        idx = Screening.objects.all().first().id
        response = self.client.delete("/screenings/{}/".format(idx), {}, format='json')
        self.assertEqual(response.status_code, 204)
        screening_ids = [screening.id for screening in Screening.objects.all()]
        self.assertNotIn(1, screening_ids)

    def test_update_screening(self):
        idx = Screening.objects.all().first().id
        response = self.client.get("/screenings/{}/".format(idx), {}, format='json')
        screening_data = response.data
        new_movie = self._random_movie()
        screening_data['movie'] = new_movie.title
        new_cinema = self._random_cinema()
        screening_data['cinema'] = new_cinema.name
        new_date = self.faker.date_time_between(start_date="now", end_date="+1y", tzinfo=timezone('Europe/Warsaw'))
        screening_data['date'] = new_date
        response = self.client.patch("/screenings/{}/".format(idx), screening_data, format='json')
        self.assertEqual(response.status_code, 200)
        screening_obj = Screening.objects.get(id=idx)
        self.assertEqual(screening_obj.movie, new_movie)
        self.assertEqual(screening_obj.cinema, new_cinema)
        self.assertEqual(screening_obj.date, new_date)
