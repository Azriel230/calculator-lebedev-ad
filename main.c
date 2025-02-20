#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

#define STACK_SIZE 100

typedef struct 
{
	int data[STACK_SIZE];
	int top;
} Stack;

void initializeStack(Stack* stack)
{
	stack->top = -1;
}

int isEmptyStack(Stack* stack)
{
	return stack->top == -1;
}

int isFullStack(Stack* stack)
{
	return stack->top == STACK_SIZE - 1;
}

void pushStack(Stack* stack, int item)
{
	if (!isFullStack(stack))
	{
		stack->top++;
		stack->data[stack->top] = item;
	}
	else
		printf("Push error! Stack is full.\n");
}

int popStack(Stack* stack)
{
	if (!isEmptyStack(stack))
	{
		int top_index = stack->top;
		stack->top--;
		return stack->data[top_index];
	}
	else
	{	
		printf("Pop error! Stack is empty.\n");
		return -1;
	}
}

int peekStack(Stack* stack)
{
	if (!isEmptyStack(stack))
	{
		return stack->data[stack->top];
	}
	else
	{	
		printf("Pop error! Stack is empty.\n");
		return -1;
	}
}

int priorityOperations(char oper)
{
	switch (oper)
	{
		case '+':
		case '-':
			return 1;
		case '*':
		case '/':
			return 2;
		default:
			return 0;
	}
}

int applyOperation(int a, int b, char oper)
{
	switch (oper)
	{
		case '+': return a + b;
		case '-': return a - b;
		case '*': return a * b;
		case '/': 
		{
			if (b != 0)
				return a / b;
			else
			{
				printf("Operation error! Division by zero! \n");
				return -1;
			}
		}
	}
}

int calculatingExpression(char* input)
{
	Stack numbers;
	initializeStack(&numbers);
	Stack operations;
	initializeStack(&operations);

	for (int i = 0; input[i] != '\0'; i++)
	{
		if (isspace(input[i]))
			continue;
		if (isdigit(input[i]))
		{
			int number = 0;
			while (isdigit(input[i]))
			{
				number = number * 10 + (input[i] - '0');
				i++;
			}
			pushStack(&numbers, number);
			i--;
		}
		else if (input[i] == '(')
		{
			pushStack(&operations, input[i]);
		}
		else if (input[i] == ')')
		{
			while (!isEmptyStack(&operations) && peekStack(&operations) != '(')
			{
				int b = popStack(&numbers);
				int a = popStack(&numbers);
				char oper = popStack(&operations);
				pushStack(&numbers, applyOperation(a, b, oper));
			}
			popStack(&operations);
		}
		else
		{
			while (!isEmptyStack(&operations) && priorityOperations(peekStack(&operations)) >= priorityOperations(input[i]))
			{
				int b = popStack(&numbers);
				int a = popStack(&numbers);
				char oper = popStack(&operations);
				pushStack(&numbers, applyOperation(a, b, oper));
			}
			pushStack(&operations, input[i]);
		}
	}

	while (!isEmptyStack(&operations))
	{
		int b = popStack(&numbers);
		int a = popStack(&numbers);
		char oper = popStack(&operations);
		pushStack(&numbers, applyOperation(a, b, oper));
	}

	return popStack(&numbers);
}

int main()
{
	char* input = malloc(1024);
	fgets(input, 1024, stdin);

	int result = calculatingExpression(input);
	printf("%d\n", result);

	free(input);
	return 0;
}
