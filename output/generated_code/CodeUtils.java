public class CodeUtils {

    /**
     * Returns the sum of two numbers.
     *
     * @param a First number
     * @param b Second number
     * @return Sum of a and b
     */
    public static double addition(double a, double b) {
        return a + b;
    }

    /**
     * Returns the difference of two numbers.
     *
     * @param a First number
     * @param b Second number
     * @return Difference of a and b (a - b)
     */
    public static double subtraction(double a, double b) {
        return a - b;
    }

    /**
     * Multiplies two numbers and returns the result.
     *
     * @param num1 The first number to be multiplied.
     * @param num2 The second number to be multiplied.
     * @return The product of the two numbers.
     */
    public static double multiplyTwoNumbers(double num1, double num2) {
        return num1 * num2;
    }



    /**
     * Divides two numbers and returns the result. Ensures proper validation to avoid division by zero.
     *
     * @param numerator   The number to be divided (dividend).
     * @param denominator The number by which the numerator is divided (divisor). Must not be zero.
     * @return The result of dividing the numerator by the denominator.
     * @throws IllegalArgumentException If the denominator is zero.
     */
    public static double divideNumbers(double numerator, double denominator) {
        // Validate that the denominator is not zero to prevent division by zero
        if (denominator == 0) {
            throw new IllegalArgumentException("Denominator must not be zero.");
        }
    
        // Perform the division and return the result
        return numerator / denominator;
    }


    /**
     * Adds two numbers and multiplies the result by two.
     *
     * @param number1 The first number to be added; must not be null.
     * @param number2 The second number to be added; must not be null.
     * @return The result of adding the two numbers and multiplying the sum by two.
     * @throws IllegalArgumentException If either number1 or number2 is null.
     */
    public static Integer addNumbersAndDouble(Integer number1, Integer number2) {
        // Validate input parameters
        if (number1 == null || number2 == null) {
            throw new IllegalArgumentException("Both number1 and number2 must not be null.");
        }

        // Perform the addition and multiplication
        int sum = number1 + number2;
        return sum * 2;
    }


    /**
     * Processes a given list of integers and returns the sum of all elements in the list.
     * 
     * @param numbers A list of integers to be summed up. Must not be null or empty.
     * @return The sum of all integers in the list.
     * @throws IllegalArgumentException If the input list is null or empty.
     */
    public static int calculateSumOfList(List<Integer> numbers) {
        // Validate input
        if (numbers == null) {
            throw new IllegalArgumentException("Input list must not be null.");
        }
        if (numbers.isEmpty()) {
            throw new IllegalArgumentException("Input list must not be empty.");
        }

        // Calculate the sum of the list
        int sum = 0;
        for (Integer number : numbers) {
            if (number != null) { // Handle potential null elements in the list
                sum += number;
            }
        }

        return sum;
    }


    /**
     * Processes the given string by validating its content and performing necessary operations.
     * This method ensures the input string is not null or empty before proceeding.
     *
     * @param input The string to be processed. Must not be null or empty.
     * @return A processed version of the input string, or an appropriate error message if validation fails.
     * @throws IllegalArgumentException if the input string is null or empty.
     */
    public static String processInputString(String input) {
        // Validate the input parameter
        if (input == null || input.trim().isEmpty()) {
            throw new IllegalArgumentException("Input string must not be null or empty.");
        }

        // Example processing logic (can be replaced with actual implementation)
        try {
            // For demonstration, let's convert the string to uppercase
            return input.toUpperCase();
        } catch (Exception e) {
            // Handle any unexpected exceptions
            throw new RuntimeException("An error occurred while processing the input string.", e);
        }
    }


    /**
     * Validates the input types for mathematical operations and raises an error if the inputs are invalid.
     * This method ensures that both inputs are non-null and of type `Number` to support operations like addition and subtraction.
     *
     * @param input1 The first input to validate, expected to be of type `Number`.
     * @param input2 The second input to validate, expected to be of type `Number`.
     * @throws IllegalArgumentException if either input is null or not an instance of `Number`.
     */
    public static void validateInputTypesForOperations(Object input1, Object input2) {
        // Check if the first input is null
        if (input1 == null) {
            throw new IllegalArgumentException("Input1 cannot be null.");
        }

        // Check if the second input is null
        if (input2 == null) {
            throw new IllegalArgumentException("Input2 cannot be null.");
        }

        // Check if the first input is of type Number
        if (!(input1 instanceof Number)) {
            throw new IllegalArgumentException("Input1 must be an instance of Number. Received: " + input1.getClass().getSimpleName());
        }

        // Check if the second input is of type Number
        if (!(input2 instanceof Number)) {
            throw new IllegalArgumentException("Input2 must be an instance of Number. Received: " + input2.getClass().getSimpleName());
        }
    }


    /**
     * Performs division of two numbers and raises an error if an attempt is made to divide by zero.
     *
     * @param numerator   The number to be divided (dividend).
     * @param denominator The number by which the numerator is divided (divisor).
     * @return The result of the division if the denominator is not zero.
     * @throws IllegalArgumentException if the denominator is zero.
     */
    public static double divideWithValidation(double numerator, double denominator) {
        // Validate that the denominator is not zero
        if (denominator == 0) {
            throw new IllegalArgumentException("Division by zero is not allowed.");
        }
    
        // Perform the division
        return numerator / denominator;
    }


    /**
     * Sums the integers in the provided list. Raises an IllegalArgumentException if the list is empty.
     *
     * @param numbers A list of integers to be summed. Must not be null or empty.
     * @return The sum of all integers in the list.
     * @throws IllegalArgumentException If the list is null or empty.
     */
    public static int sumNonEmptyList(List<Integer> numbers) {
        // Validate that the input list is not null
        if (numbers == null) {
            throw new IllegalArgumentException("The input list cannot be null.");
        }

        // Validate that the input list is not empty
        if (numbers.isEmpty()) {
            throw new IllegalArgumentException("The input list cannot be empty.");
        }

        // Calculate and return the sum of the list
        int sum = 0;
        for (int number : numbers) {
            sum += number;
        }
        return sum;
    }


    /**
     * Sums the elements of a list, ensuring all elements are numeric. 
     * If the list contains any non-numeric elements, an IllegalArgumentException is raised.
     *
     * @param elements A list of objects to be summed. All elements must be instances of Number.
     * @return The sum of all numeric elements in the list as a double.
     * @throws IllegalArgumentException If the list contains non-numeric elements or is null.
     */
    public static double sumNumericElements(List<Object> elements) {
        // Validate input
        if (elements == null) {
            throw new IllegalArgumentException("The input list cannot be null.");
        }

        double sum = 0.0;

        for (Object element : elements) {
            if (!(element instanceof Number)) {
                throw new IllegalArgumentException("The list contains a non-numeric element: " + element);
            }
            sum += ((Number) element).doubleValue();
        }

        return sum;
    }


    /**
     * Provides a command-line interface to demonstrate all calculator operations, including addition and subtraction.
     * Prompts the user to select an operation, input numbers, and displays the result.
     *
     * @param scanner A pre-initialized {@link java.util.Scanner} object for reading user input.
     * @throws IllegalArgumentException If the provided scanner is null.
     */
    public static void demonstrateCalculatorOperations(Scanner scanner) {
        // Validate the input parameter
        if (scanner == null) {
            throw new IllegalArgumentException("Scanner object cannot be null.");
        }

        System.out.println("Welcome to the Calculator CLI!");
        System.out.println("Available operations:");
        System.out.println("1. Addition");
        System.out.println("2. Subtraction");
        System.out.println("3. Exit");

        while (true) {
            try {
                System.out.print("Please select an operation (1-3): ");
                int choice = Integer.parseInt(scanner.nextLine().trim());

                if (choice == 3) {
                    System.out.println("Exiting the Calculator CLI. Goodbye!");
                    break;
                }

                if (choice < 1 || choice > 3) {
                    System.out.println("Invalid choice. Please select a valid operation (1-3).");
                    continue;
                }

                System.out.print("Enter the first number: ");
                double num1 = Double.parseDouble(scanner.nextLine().trim());

                System.out.print("Enter the second number: ");
                double num2 = Double.parseDouble(scanner.nextLine().trim());

                double result;
                switch (choice) {
                    case 1: // Addition
                        result = addition(num1, num2);
                        System.out.println("Result of addition: " + result);
                        break;
                    case 2: // Subtraction
                        result = subtraction(num1, num2);
                        System.out.println("Result of subtraction: " + result);
                        break;
                    default:
                        System.out.println("Unexpected error occurred.");
                }
            } catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter numeric values only.");
            } catch (Exception e) {
                System.out.println("An error occurred: " + e.getMessage());
            }
        }
    }
