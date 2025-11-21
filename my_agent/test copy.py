import math
from typing import Optional

class Factorial:
    """
    A class to calculate the factorial of a non-negative integer.

    Attributes:
        number (int): The integer for which the factorial is to be calculated.
    """

    def __init__(self, n: int):
        """
        Initializes the Factorial object with a given number.

        Args:
            n (int): The non-negative integer to calculate the factorial for.

        Raises:
            ValueError: If n is negative.
            TypeError: If n is not an integer.
        """
        if not isinstance(n, int):
            raise TypeError("Input must be an integer.")
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers.")
        self._number: int = n
        self._factorial_result: Optional[int] = None # Cache the result

    @property
    def number(self) -> int:
        """Returns the number for which the factorial is calculated."""
        return self._number

    def calculate(self) -> int:
        """
        Calculates the factorial of the stored number.
        Uses an iterative approach for efficiency and to avoid recursion depth limits.

        Returns:
            int: The factorial of the number.
        """
        if self._factorial_result is not None:
            return self._factorial_result # Return cached result

        if self._number == 0:
            self._factorial_result = 1
        else:
            result = 1
            for i in range(1, self._number + 1):
                result *= i
            self._factorial_result = result
        return self._factorial_result

    def __call__(self) -> int:
        """
        Makes the instance callable, so calling the object calculates the factorial.

        Returns:
            int: The factorial of the number.
        """
        return self.calculate()

    def __str__(self) -> str:
        """
        Returns a string representation of the Factorial object.
        """
        return f"Factorial for {self.number}"

    def __repr__(self) -> str:
        """
        Returns a more detailed string representation for developers.
        """
        return f"Factorial(n={self.number})"

    def __eq__(self, other: object) -> bool:
        """
        Checks if two Factorial objects are equal based on their numbers.

        Args:
            other (object): The other object to compare with.

        Returns:
            bool: True if the objects represent the factorial of the same number, False otherwise.
        """
        if not isinstance(other, Factorial):
            return NotImplemented
        return self.number == other.number

    def __hash__(self) -> int:
        """
        Computes the hash of the Factorial object based on its number.
        This allows Factorial objects to be used in sets or as dictionary keys.

        Returns:
            int: The hash value of the object.
        """
        return hash(self.number)

    def using_math_module(self) -> int:
        """
        Calculates the factorial using Python's built-in math.factorial function.
        This method is provided for comparison/demonstration.

        Returns:
            int: The factorial of the number.
        """
        # Our __init__ already validates for n < 0, so this check is technically
        # redundant in a well-constructed object, but harmless if the object
        # state were somehow corrupted externally.
        if self._number < 0:
            raise ValueError("math.factorial() not defined for negative values")
        return math.factorial(self._number)


if __name__ == "__main__":
    print("--- Factorial Class Demonstration ---")

    # Example 1: Calculate factorial of a positive number
    try:
        f5 = Factorial(5)
        print(f"Object: {f5}")
        print(f"Factorial of {f5.number} (using calculate method): {f5.calculate()}")
        print(f"Factorial of {f5.number} (calling object directly): {f5()}")
        print(f"Factorial of {f5.number} (using math.factorial): {f5.using_math_module()}")

        print("\n--- Testing caching ---")
        # The result should be cached, so subsequent calls are faster
        print(f"Recalculating factorial for {f5.number}: {f5.calculate()}")
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")

    # Example 2: Factorial of 0
    try:
        f0 = Factorial(0)
        print(f"\nFactorial of {f0.number}: {f0.calculate()}")
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")

    # Example 3: Invalid input - negative number
    try:
        f_neg = Factorial(-3)
        print(f"Factorial of {f_neg.number}: {f_neg.calculate()}")
    except (ValueError, TypeError) as e:
        print(f"Attempted Factorial(-3): Caught error: {e}")

    # Example 4: Invalid input - non-integer
    try:
        f_float = Factorial(4.5)
        print(f"Factorial of {f_float.number}: {f_float.calculate()}")
    except (ValueError, TypeError) as e:
        print(f"Attempted Factorial(4.5): Caught error: {e}")

    # Example 5: Larger number
    try:
        f10 = Factorial(10)
        print(f"\nFactorial of {f10.number}: {f10.calculate()}")
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")

    # Example 6: Direct call to object
    f4 = Factorial(4)
    print(f"\nDirect call for Factorial(4): {f4()}")

    # Example 7: Testing __eq__ and __hash__
    print("\n--- Testing __eq__ and __hash__ ---")
    f_five_a = Factorial(5)
    f_five_b = Factorial(5)
    f_six = Factorial(6)

    print(f"f_five_a == f_five_b: {f_five_a == f_five_b}")  # Should be True
    print(f"f_five_a == f_six: {f_five_a == f_six}")        # Should be False
    print(f"f_five_a == 5: {f_five_a == 5}")                # Should be False (or NotImplemented, then False)

    factorial_set = {f_five_a, f_six, f_five_b}
    print(f"Set of factorials: {factorial_set}") # Should only contain 2 unique objects based on number

    try:
        f_invalid_hash = Factorial("not a number")
    except TypeError as e:
        print(f"Attempted Factorial('not a number'): Caught error: {e}")


    print("\n--- End of Demonstration ---")
