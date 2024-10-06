from bot.routines.goats import GOATSRoutine

def test_goats():
    settings = {
        'login_url': 'https://example.com/login',
        'username': 'testuser',
        'password': 'testpass'
    }
    routine = GOATSRoutine(settings)
    result = routine.run()
    print(result)

if __name__ == "__main__":
    test_goats()