import datetime
import mysql.connector
from typing import Dict, Optional, Tuple, Any, List


class DatabaseHandler:
    """
    Handles database operations for the property listings.
    """

    def __init__(self, host='localhost', port=3306, user='user', password='password', database='RC'):
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }

    def connect(self):
        """Establishes a connection to the MySQL database."""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL database: {err}")
            return None

    def __get_connection(self):
        """Establishes a connection to the MySQL database."""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL database: {err}")
            return None

    def listing_exists(self, listing_id: int) -> Optional[Tuple]:
        """
        Checks if a listing already exists in the database.
        Returns the listing data if it exists, None otherwise.
        """
        connection = self.connect()
        if not connection:
            return None

        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM LISTING WHERE ID = %s"
            cursor.execute(query, (listing_id,))
            result = cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(f"Error checking if listing exists: {err}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def insert_listing(self, property_details: Dict) ->  Optional[int]:
        """
        Inserts a new listing into the database.
        Returns True if successful, False otherwise.
        """
        if not all(key in property_details for key in ['url', 'original_price', 'created_at']):
            print("Missing required fields for listing insertion")
            return False

        connection = self.connect()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Prepare query with only the fields that exist in property_details
            fields = []
            values = []
            placeholders = []

            for field in ['URL', 'DESCRIPTION', 'NUMBER_OF_ROOMS', 'TOTAL_AREA',
                          'FLOOR', 'CREATED_AT', 'LAST_CHECKED_AT', 'ORIGINAL_PRICE', 'SOURCE_WEBSITE']:
                # Convert field name to property_details key (lowercase)
                key = field.lower()

                if key in property_details and property_details[key] is not None:
                    fields.append(field)
                    values.append(property_details[key])
                    placeholders.append('%s')

            query = f"INSERT INTO LISTING ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, values)
            connection.commit()
            # Get the auto-generated ID
            last_insert_id = cursor.lastrowid

            connection.commit()
            return last_insert_id
        except mysql.connector.Error as err:
            print(f"Error inserting listing: {err}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def update_listing(self, listing_id: int, property_details: Dict) -> bool:
        """
        Updates an existing listing in the database.
        Returns True if successful, False otherwise.
        """
        connection = self.connect()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Prepare update query
            update_parts = []
            values = []

            for field in ['URL', 'DESCRIPTION', 'NUMBER_OF_ROOMS', 'TOTAL_AREA',
                          'FLOOR', 'LAST_CHECKED_AT', 'ORIGINAL_PRICE', 'SOURCE_WEBSITE']:
                # Convert field name to property_details key (lowercase)
                key = field.lower()

                if key in property_details and property_details[key] is not None:
                    update_parts.append(f"{field} = %s")
                    values.append(property_details[key])

            # Only update if there's something to update
            if not update_parts:
                return True

            # Add listing_id to values list
            values.append(listing_id)

            query = f"UPDATE LISTING SET {', '.join(update_parts)} WHERE ID = %s"
            cursor.execute(query, values)
            connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error updating listing: {err}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_price_history(self, listing_id: int, price: int) -> bool:
        """
        Adds a new price history record for a listing.
        Returns True if successful, False otherwise.
        """
        connection = self.connect()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Get the next available ID for price_history
            cursor.execute("SELECT MAX(ID) FROM PRICE_HISTORY")
            result = cursor.fetchone()
            next_id = 1 if result[0] is None else result[0] + 1

            query = "INSERT INTO PRICE_HISTORY (ID, LISTING_ID, PRICE, RECORDED_AT) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (next_id, listing_id, price, datetime.datetime.now()))
            connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error adding price history: {err}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def update_availability(self, listing_id: int, is_available: bool) -> bool:
        """
        Updates the availability history for a listing.
        Returns True if successful, False otherwise.
        """
        connection = self.connect()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Get the current availability status
            cursor.execute("""
                SELECT IS_AVAILABLE 
                FROM AVAILABILITY_HISTORY 
                WHERE LISTING_ID = %s 
                ORDER BY CHANGED_AT DESC 
                LIMIT 1
            """, (listing_id,))

            result = cursor.fetchone()
            current_availability = None if result is None else bool(result[0])

            # Only add a new record if availability has changed or there is no record yet
            if current_availability is None or current_availability != is_available:
                # Get the next available ID
                cursor.execute("SELECT MAX(ID) FROM AVAILABILITY_HISTORY")
                result = cursor.fetchone()
                next_id = 1 if result[0] is None else result[0] + 1

                query = """
                    INSERT INTO AVAILABILITY_HISTORY (ID, LISTING_ID, IS_AVAILABLE, CHANGED_AT) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (next_id, listing_id, is_available, datetime.datetime.now()))
                connection.commit()

            return True
        except mysql.connector.Error as err:
            print(f"Error updating availability: {err}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def log_scraping_error(self, listing_id: int, error_message: str) -> bool:
        """
        Logs a scraping error for a listing.
        Returns True if successful, False otherwise.
        """
        connection = self.connect()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Get the next available ID
            cursor.execute("SELECT MAX(ID) FROM SCRAPPING_ERROR")
            result = cursor.fetchone()
            next_id = 1 if result[0] is None else result[0] + 1

            query = """
                INSERT INTO SCRAPPING_ERROR 
                (ID, LISTING_ID, ERROR_MESSAGE, OCCURRED_AT) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (next_id, listing_id, error_message, datetime.datetime.now()))
            connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error logging scraping error: {err}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def create_verification_token(
            self,
            email: str,
            token: str,
            expiration_datetime: datetime,
            status: str = "pending"
    ) -> int:
        """
        Store a new verification token in the database with status

        Args:
            email: User's email address
            token: Randomly generated verification token
            expiration_datetime: When this token should expire
            status: Initial status (default: pending)

        Returns:
            int: ID of the created token record or 0 on failure
        """
        query: str = """
        INSERT INTO EMAIL_VERIFICATION_TOKENS 
        (EMAIL, TOKEN, EXPIRES_AT, STATUS) 
        VALUES (%s, %s, %s, %s)
        """

        connection = self.connect()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            cursor.execute(query, (email, token, expiration_datetime, status))
            token_id: int = cursor.lastrowid
            connection.commit()
            return token_id
        except Exception as e:
            print(f"Error creating verification token: {e}")
            return 0

    def get_verification_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve token data if it exists and is valid

        Args:
            token: The verification token string

        Returns:
            Optional[Dict[str, Any]]: Token data including email and expiration,
                                     or None if token not found
        """
        query = """
        SELECT EMAIL, EXPIRES_AT, USED 
        FROM EMAIL_VERIFICATION_TOKENS 
        WHERE TOKEN = %s
        """

        try:
            with self.__get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (token,))
                    result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Error retrieving verification token: {e}")
            return None

    def mark_token_as_used(self, token: str) -> bool:
        """
        Mark a token as used after successful verification

        Args:
            token: The verification token to mark as used

        Returns:
            bool: Success or failure of the operation
        """
        query = """
        UPDATE EMAIL_VERIFICATION_TOKENS 
        SET USED = TRUE 
        WHERE TOKEN = %s
        """

        try:
            with self.__get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (token,))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error marking token as used: {e}")
            return False

    def cleanup_expired_tokens(self) -> bool:
        """
        Delete tokens that have expired (can be run periodically)

        Returns:
            bool: Success or failure of the operation
        """
        query = """
        DELETE FROM EMAIL_VERIFICATION_TOKENS 
        WHERE EXPIRES_AT < NOW()
        """

        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                conn.commit()
            return True
        except Exception as e:
            print(f"Error cleaning up expired tokens: {e}")
            return False

    def update_email_status(
            self,
            email: Optional[str] = None,
            token: Optional[str] = None,
            token_id: Optional[int] = None,
            status: Optional[str] = None,
            error_message: Optional[str] = None
    ) -> bool:
        """
        Update the status of an email verification token

        Args:
            email: User's email (optional if token or token_id provided)
            token: The verification token (optional if email or token_id provided)
            token_id: The token record ID (optional if email or token provided)
            status: New status value
            error_message: Error details if status is 'failed'

        Returns:
            bool: Success or failure of the update operation
        """
        # Build where clause based on provided parameters
        where_clause: str = ""
        params: List[Any] = []

        if token_id:
            where_clause = "ID = %s"
            params.append(token_id)
        elif token:
            where_clause = "TOKEN = %s"
            params.append(token)
        elif email:
            # This would get the most recent token for this email
            where_clause = "EMAIL = %s ORDER BY CREATED_AT DESC LIMIT 1"
            params.append(email)
        else:
            return False  # Need at least one identifier

        # Build update clause
        update_parts: List[str] = []
        if status:
            update_parts.append("STATUS = %s")
            params.append(status)

        if error_message and status == 'failed':
            update_parts.append("ERROR_MESSAGE = %s")
            params.append(error_message)

        if not update_parts:
            return False  # Nothing to update

        # Create full query
        query: str = f"UPDATE EMAIL_VERFICATION_TOKENS SET {', '.join(update_parts)} WHERE {where_clause}"

        try:
            with self.__get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    updated: bool = cursor.rowcount > 0
                conn.commit()
            return updated
        except Exception as e:
            print(f"Error updating email status: {e}")
            return False

    def get_verification_status(self, token_id: int) -> Optional[str]:
        """
        Get the current status of a verification token

        Args:
            token_id: The ID of the token record

        Returns:
            Optional[str]: Status value ('pending', 'sent', 'failed') or None if not found
        """
        query: str = "SELECT STATUS FROM EMAIL_VERIFICATION_TOKENS WHERE id = %s"

        try:
            with self.__get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (token_id,))
                    result: Optional[tuple] = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting verification status: {e}")
            return None

    def get_verification_error(self, token_id: int) -> Optional[str]:
        """
        Get the error message for a failed verification token

        Args:
            token_id: The ID of the token record

        Returns:
            Optional[str]: Error message or None if not found
        """
        query: str = "SELECT ERROR_MESSAGE FROM EMAIL_VERIFICATION_TOKENS WHERE ID = %s AND STATUS = 'failed'"

        try:
            with self.__get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (token_id,))
                    result: Optional[tuple] = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting verification error: {e}")
            return None