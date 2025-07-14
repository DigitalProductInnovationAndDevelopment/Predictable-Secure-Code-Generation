import java.util.*;

/**
 * Utility class providing basic mathematical and string/list processing methods.
 */
public class CodeUtilsUpdate {

    /**
     * Return the sum of two numbers.
     *
     * @param a First number (int or float equivalent)
     * @param b Second number (int or float equivalent)
     * @return Sum of a and b
     */
    public static double addition(double a, double b) {
        return a + b;
    }

    /**
     * Return the difference of two numbers (a - b).
     *
     * @param a First number (int or float equivalent)
     * @param b Second number (int or float equivalent)
     * @return Difference of a and b
     */
    public static double subtraction(double a, double b) {
        return a - b;
    }

    /**
     * Multiply two numbers and return the product.
     *
     * @param num1 First number (int or float equivalent)
     * @param num2 Second number (int or float equivalent)
     * @return Product of num1 and num2
     */
    public static double multiplyTwoNumbers(double num1, double num2) {
        return num1 * num2;
    }

    /**
     * Divide two numbers and return the quotient.
     *
     * @param numerator Number to be divided (dividend)
     * @param denominator Number by which to divide (divisor)
     * @return Result of the division
     * @throws IllegalArgumentException If denominator is zero
     */
    public static double divideTwoNumbers(double numerator, double denominator) {
        if (denominator == 0) {
            throw new IllegalArgumentException("Division by zero is not allowed.");
        }
        return numerator / denominator;
    }

    /**
     * Adds two numbers and multiplies the result by two.
     *
     * @param num1 First number (int or float equivalent)
     * @param num2 Second number (int or float equivalent)
     * @return (num1 + num2) * 2
     */
    public static double addAndMultiplyByTwo(double num1, double num2) {
        return (num1 + num2) * 2;
    }

    /**
     * Calculate the sum of all elements in a given list.
     *
     * @param numbers List of numeric values to be summed
     * @return Sum of all elements in the list
     * @throws IllegalArgumentException If list is null, empty, or contains null elements
     */
    public static double sumListElements(List<Double> numbers) {
        if (numbers == null || numbers.isEmpty()) {
            throw new IllegalArgumentException("The list cannot be null or empty.");
        }
        double sum = 0;
        for (Double num : numbers) {
            if (num == null) throw new IllegalArgumentException("List contains null elements.");
            sum += num;
        }
        return sum;
    }

    /**
     * Determines whether a given string is a palindrome, ignoring case and non-alphanumeric characters.
     *
     * @param input String to check
     * @return true if the input is a palindrome, false otherwise
     * @throws IllegalArgumentException If the input is null
     */
    public static boolean isPalindrome(String input) {
        if (input == null) {
            throw new IllegalArgumentException("Input must be a non-null string.");
        }

        StringBuilder normalized = new StringBuilder();
        for (char ch : input.toLowerCase().toCharArray()) {
            if (Character.isLetterOrDigit(ch)) {
                normalized.append(ch);
            }
        }

        String normalizedStr = normalized.toString();
        String reversedStr = normalized.reverse().toString();
        return normalizedStr.equals(reversedStr);
    }

    /**
     * Validates that the operation name is supported.
     *
     * @param operationName Name of the operation (e.g., "addition", "subtraction")
     * @param param1 First parameter (unused in validation)
     * @param param2 Second parameter (unused in validation)
     * @throws IllegalArgumentException If operationName is null or unsupported
     */
    public static void validateOperationInputs(String operationName, double param1, double param2) {
        Set<String> validOperations = new HashSet<>(Arrays.asList("addition", "subtraction"));
        if (operationName == null || !validOperations.contains(operationName)) {
            throw new IllegalArgumentException("Unsupported operation: " + operationName);
        }
    }

    /**
     * Safely performs division, raising an error if the denominator is zero.
     *
     * @param numerator Number to be divided (dividend)
     * @param denominator Number by which to divide (divisor)
     * @return Result of the division
     * @throws IllegalArgumentException If denominator is zero
     */
    public static double safeDivision(double numerator, double denominator) {
        if (denominator == 0) {
            throw new IllegalArgumentException("Division by zero is not allowed.");
        }
        return numerator / denominator;
    }

    /**
     * Sums the elements of a non-empty list.
     *
     * @param numbers List of numeric values
     * @return Sum of values in the list
     */
    public static double sumNonEmptyList(List<Double> numbers) {
        return sumListElements(numbers);
    }

    /**
     * Sums numeric elements in a list.
     *
     * @param elements List of numeric elements
     * @return Sum of values in the list
     */
    public static double sumNumericElements(List<Double> elements) {
        return sumListElements(elements);
    }

    /**
     * Processes a list by sorting it.
     *
     * @param inputList List of values to process
     * @return New sorted list
     * @throws IllegalArgumentException If inputList is null or contains null
     */
    public static List<Double> processList(List<Double> inputList) {
        if (inputList == null || inputList.contains(null)) {
            throw new IllegalArgumentException("Invalid list: null or contains null elements.");
        }
        List<Double> sortedList = new ArrayList<>(inputList);
        Collections.sort(sortedList);
        return sortedList;
    }

    /**
     * Returns the input string as-is after validation.
     *
     * @param inputString String to process
     * @return The same string
     * @throws IllegalArgumentException If inputString is null
     */
    public static String processString(String inputString) {
        if (inputString == null) {
            throw new IllegalArgumentException("The input must be a string.");
        }
        return inputString;
    }

    /**
     * Provides a simple command-line interface to exercise addition and subtraction.
     */
    public static void demonstrateCalculatorOperations() {
        Scanner scanner = new Scanner(System.in);
        while (true) {
            System.out.println("\nCalculator Operations:");
            System.out.println("1. Addition");
            System.out.println("2. Subtraction");
            System.out.println("3. Exit");
            System.out.print("Select an operation (1/2/3): ");
            String choice = scanner.nextLine();

            switch (choice) {
                case "1" -> {
                    System.out.print("Enter the first number: ");
                    double a1 = scanner.nextDouble();
                    System.out.print("Enter the second number: ");
                    double b1 = scanner.nextDouble();
                    scanner.nextLine(); // consume newline
                    System.out.println("Result: " + addition(a1, b1));
                }
                case "2" -> {
                    System.out.print("Enter the first number: ");
                    double a2 = scanner.nextDouble();
                    System.out.print("Enter the second number: ");
                    double b2 = scanner.nextDouble();
                    scanner.nextLine(); // consume newline
                    System.out.println("Result: " + subtraction(a2, b2));
                }
                case "3" -> {
                    System.out.println("Exiting calculator. Goodbye!");
                    scanner.close();
                    return;
                }
                default -> System.out.println("Invalid choice. Please try again.");
            }
        }
    }

    /**
     * Main method demonstrating basic operations and CLI.
     *
     * @param args Command-line arguments (unused)
     */
    public static void main(String[] args) {
        System.out.println("Addition: 5 + 3 = " + addition(5, 3));
        System.out.println("Subtraction: 5 - 3 = " + subtraction(5, 3));
        System.out.println("Addition: 10.5 + 2.3 = " + addition(10.5, 2.3));
        System.out.println("Subtraction: 10.5 - 2.3 = " + subtraction(10.5, 2.3));

        // Uncomment to try CLI
        demonstrateCalculatorOperations();
    }
}
