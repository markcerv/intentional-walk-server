from django.test import Client, TestCase

from .utils import Login, generate_test_data


class TestAdminViews(TestCase):
    contest0_id = None

    @classmethod
    def setUpTestData(cls):
        cls.contest0_id = generate_test_data()

    def test_get_me(self):
        c = Client()
        # when unauthenticated, returns an empty response
        response = c.get("/api/admin/me")
        self.assertEqual(response.status_code, 204)

        # log in
        self.assertTrue(Login.login(c))

        # when authenticated, returns the JSON representation of the user
        response = c.get("/api/admin/me")
        data = response.json()
        self.assertEqual(data["username"], "testadmin")

    def test_get_home(self):
        c = Client()
        self.assertTrue(Login.login(c))
        response = c.get("/api/admin/home")
        data = response.json()
        self.assertEqual(
            data,
            {
                "accounts_count": 5,  # 6 accounts - 1 tester
                "accounts_steps": 350000,  # 14 days * (10,000 + 15,000 steps/day)
                "accounts_distance": 280000,  # 14 days * (8,000 + 12,000 meters/day)
            },
        )

    def test_get_contests(self):
        c = Client()
        self.assertTrue(Login.login(c))
        response = c.get("/api/admin/contests")
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["contest_id"], self.contest0_id)

    def test_get_users(self):
        c = Client()
        self.assertTrue(Login.login(c))
        response = c.get("/api/admin/users")
        data = response.json()
        self.assertEqual(len(data), 5)  # 6 accounts - 1 tester

        response = c.get(f"/api/admin/users?contest_id={self.contest0_id}")
        data = response.json()
        self.assertEqual(len(data), 4)  # 5 accounts in the contest - 1 tester
        # default ordering is by name
        self.assertEqual(data[0]["name"], "User 2")
        self.assertEqual(data[0]["is_new"], False)
        self.assertEqual(data[0]["dw_count"], 7)
        self.assertEqual(data[0]["dw_steps"], 70000)
        self.assertEqual(data[0]["dw_distance"], 56000)
        self.assertEqual(data[1]["name"], "User 3")
        self.assertEqual(data[1]["is_new"], True)
        self.assertEqual(data[1]["dw_count"], 7)
        self.assertEqual(data[1]["dw_steps"], 105000)
        self.assertEqual(data[1]["dw_distance"], 84000)
        self.assertEqual(data[2]["name"], "User 4")
        self.assertEqual(data[2]["is_new"], True)
        self.assertEqual(data[2]["dw_count"], 0)
        self.assertEqual(data[2]["dw_steps"], None)
        self.assertEqual(data[2]["dw_distance"], None)
        self.assertEqual(data[3]["name"], "User 5")
        self.assertEqual(data[3]["is_new"], True)
        self.assertEqual(data[3]["dw_count"], 0)
        self.assertEqual(data[3]["dw_steps"], None)
        self.assertEqual(data[3]["dw_distance"], None)

        response = c.get(
            f"/api/admin/users?contest_id={self.contest0_id}&is_tester=true"
        )
        data = response.json()
        self.assertEqual(len(data), 1)  # 1 tester

    def test_get_users_by_zip(self):
        c = Client()
        self.assertTrue(Login.login(c))
        response = c.get(f"/api/admin/users/zip?contest_id={self.contest0_id}")
        data = response.json()
        self.assertEqual(
            data,
            {
                "total": {"94103": 2, "94104": 2},
                "new": {"94103": 1, "94104": 2},
            },
        )

    def test_get_users_active_by_zip(self):
        c = Client()
        self.assertTrue(Login.login(c))
        response = c.get(
            f"/api/admin/users/zip/active?contest_id={self.contest0_id}"
        )
        data = response.json()
        self.assertEqual(
            data,
            {
                "total": {"94103": 2, "94104": 1},
                "new": {"94103": 1, "94104": 1},
            },
        )

    def test_get_users_median_steps_by_zip(self):
        c = Client()
        self.assertTrue(Login.login(c))
        response = c.get(
            f"/api/admin/users/zip/steps?contest_id={self.contest0_id}"
        )
        data = response.json()
        self.assertEqual(
            data,
            {
                "all": 87500.0,
                "94103": 87500.0,
            },  # median of [70k, 105k] = avg of the two = 87.5k
        )
