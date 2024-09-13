from app import create_app

app = create_app()

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)


