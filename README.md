# MedSys - Automated System for Medical Institutions

MedSys is an automated system designed to manage operations within medical institutions. This system facilitates the management of patient records, doctor profiles, appointments, and other critical aspects of healthcare administration. Built using Django and Django REST Framework, MedSys leverages modern web technologies to provide a robust and scalable solution for healthcare providers.

## Features

- **User Management**: Create and manage user profiles for doctors, patients, and administrative staff.
- **Appointments**: Schedule, update, and track patient appointments with doctors.
- **Medical Records**: Maintain detailed records of patient diagnoses and treatments.
- **Specializations**: Assign and manage doctor specializations to ensure accurate matching with patient needs.
- **Multi-language Support**: Localization and internationalization for a global user base.

## Technologies Used

- **Django**: High-level Python web framework that encourages rapid development and clean, pragmatic design.
- **PostgreSQL**: Powerful, open-source object-relational database system.
- **Django REST Framework**: Flexible and powerful toolkit for building Web APIs.
- **Docker**: Platform for developing, shipping, and running applications in containers.
- **Docker Compose**: Tool for defining and running multi-container Docker applications.

## Installation

### Prerequisites

- Docker and Docker Compose installed on your machine.

### Setup with Docker

1. **Clone the repository**:
   ```sh
   git clone https://github.com/argunv/medsys.git
   cd medsys
   ```

2. **Create a `.env` file**:
   ```env
   POSTGRES_DB=
   POSTGRES_USER=
   POSTGRES_PASSWORD=
   POSTGRES_PORT=

   DJANGO_PORT=

   DEBUG=
   SECRET_KEY=
   POSTGRES_HOST=
   ```
   You can find an example with values in the [`.env.example`](https://github.com/argunv/medsys/blob/main/.env.example) file.

3. **Build and run the Docker containers**:
   ```sh
   docker-compose up -d
   ```

   This will build and start the PostgreSQL and Django containers. The Django application will automatically apply database migrations, create a superuser, and start the development server.

4. **Access the system**:
   - Open your browser and navigate to `http://127.0.0.1:${DJANGO_PORT}/` (e.g., `http://127.0.0.1:8000/`).

## Usage

1. **Admin Panel**:
   Use the admin panel to manage users, appointments, and other data. Access it via `http://127.0.0.1:${DJANGO_PORT}/admin/`.
   Default login: `admin`, password: `admin`.

2. **API Endpoints**:
   - View the available API endpoints by visiting `http://127.0.0.1:${DJANGO_PORT}/api/`.

3. **Token Authentication**:
   - Get your TOKEN sending POST request to `http://127.0.0.1:${DJANGO_PORT}/api-token-auth/`.

## Running Tests

To run the test suite, use the following command:
```sh
python app/manage.py test clinic.tests
```

If using Docker, you can run tests inside the container:
```sh
docker-compose exec web python app/manage.py test clinic.tests
```

## Code Style and Contribution Guidelines

- The project follows PEP8 standards, with additional configurations specified in `setup.cfg`.
- We use `flake8`, `wemake-python-styleguide`, and `bandit` for linting and security checks.
- Contributions are welcome! Please make sure your code adheres to the existing style guide and that all tests pass.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Additional Information

- **Templates and Static Files**: The project includes a variety of HTML templates and static assets (CSS, JS, images) located in the `templates` and `clinic/static` directories.
- **Contact Information**: For questions or support, please contact [v_argun@inbox.ru].

---

Thank you for using MedSys! We hope it helps streamline your medical institution's operations.
