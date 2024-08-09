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

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL

### Setup

1. **Clone the repository**:
   ```sh
   git clone https://github.com/argunv/medsys.git
   cd medsys
   ```

2. **Create a virtual environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the `app` directory**:
   Here's an example of what the `.env` file should look like:
   ```env
   POSTGRES_DB=
   POSTGRES_USER=
   POSTGRES_PASSWORD=
   POSTGRES_PORT=

   DEBUG=
   SECRET_KEY=
   POSTGRES_HOST=

   DJANGO_PORT=
   ```

5. **Apply database migrations**:
   ```sh
   python app/manage.py migrate
   ```

6. **Create a superuser**:
   ```sh
   python app/manage.py createsuperuser
   ```

7. **Run the development server**:
   ```sh
   python app/manage.py runserver
   ```

## Usage

1. **Access the system**: 
   Open your browser and navigate to `http://127.0.0.1:8000/`.

2. **Admin Panel**:
   Use the admin panel to manage users, appointments, and other data. Access it via `http://127.0.0.1:8000/admin/`.

3. **API Endpoints**:
   - View the available API endpoints by visiting `http://127.0.0.1:8000/api/`.

## Running Tests

To run the test suite, use the following command:
```sh
python app/manage.py test
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
