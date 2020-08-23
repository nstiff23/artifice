#include <iostream>
#include <string>
#include <regex>
#include <algorithm>
#include <list>
#include <vector>
#include <chrono>

#include <time.h>
#include <stdlib.h>

// maintains debug and error logs
class Log {
public:
	enum Level {
		error, eval, parser, tokenizer, all
	};
private:
	static Level log_level;
	static int indentation;
public:
	static void set_level(Level lvl) {
		log_level = lvl;
	}
	static void indent() {
		indentation++;
	}
	static void unindent() {
		if (indentation > 0)
			indentation--;
	}
//
	static void log_msg(std::string msg, Level lvl) {
		if (log_level >= lvl) {
			std::string indent = "";
			for (int i = 0; i < indentation; i++) {
				indent += "    ";
			}
//
			std::string prefix;
			if (lvl == Level::error)
				prefix = "[ERROR] ";
			if (lvl == Level::tokenizer)
				prefix = "[TOKENIZER] ";
			if (lvl == Level::parser)
				prefix = "[PARSER] ";
			if (lvl == eval)
				prefix = "[EVALUATION] ";
//
			std::cout << prefix << indent << msg << '\n';
		}
	}
};
// initializes log variables
Log::Level Log::log_level = Log::Level::all;
int Log::indentation = 0;
// interface for all expressions
// an expression is an atomic operation, number, or dice roll that can evaluate to a long
class Expr {
public:
	virtual long eval() = 0;
};
// all atomic operations are children of Expr2
class Expr2 : public Expr {
public:
	Expr *e1, *e2;
	Expr2(Expr *ex1, Expr *ex2) {
		e1 = ex1;
		e2 = ex2;
	}
};

class Roll : public Expr {
private:
	int num; //the number of dice to roll
	int die; //the maximum of each die
	int highest; //the number of highest rolls to keep

public:
	Roll(int number, int die_val, int num_highest) {
		if (number <= 0) {
			Log::log_msg("Can't roll fewer than 1 dice!", Log::Level::error);
		}
		if (num_highest >= number) {
			Log::log_msg("Can't keep the highest " + std::to_string(highest) + " rolls when only " + std::to_string(num) + " dice are rolled!", Log::Level::error);
		}
		num = number;
		die = die_val;
		highest = num_highest;
	}

//this method returns the result of the roll
	long eval () override {
		if (die <= 0) {
			return num;
		}
		std::vector<int> rolls(num);
		for (int i = 0; i < num; i++) {
			rolls[i] = rand() % die + 1;
		}
//
		if (highest > 0) {
			int drop = num - highest;
			std::partial_sort(rolls.begin(), rolls.end() - highest, rolls.end());
			for (int i = 0; i < drop; i++) {
				rolls[i] = 0;
			}
		}
//
		long sum{ 0 };
		for (int i = 0; i < num; i++) {
			sum += rolls[i];
		}
//
		Log::log_msg("Rolling " + std::to_string(num) + "d" + std::to_string(die) + "h" + std::to_string(highest) + ": " + std::to_string(sum), Log::Level::eval);
		return sum;
	}
};
// multiplies two expressions
class Mul : public Expr2 {
public:
	long eval() override {
		long v1 = e1->eval();
		long v2 = e2->eval();
		Log::log_msg(std::to_string(v1) + "*" + std::to_string(v2) + "=" + std::to_string(v1 * v2), Log::Level::eval);
		return (v1 * v2);
	}
	Mul(Expr *e1, Expr *e2) :Expr2(e1, e2) {}
};
// divides two expressions
class Div : public Expr2 {
public:
	long eval() override {
		long v1 = e1->eval();
		long v2 = e2->eval();
		Log::log_msg(std::to_string(v1) + "/" + std::to_string(v2) + "=" + std::to_string(v1 / v2), Log::Level::eval);
		return (v1 / v2);
	}
	Div(Expr *e1, Expr *e2) :Expr2(e1, e2) {}
};
// adds two expressions
class Add : public Expr2 {
public:
	long eval() override {
		long v1 = e1->eval();
		long v2 = e2->eval();
		Log::log_msg(std::to_string(v1) + "+" + std::to_string(v2) + "=" + std::to_string(v1 + v2), Log::Level::eval);
		return (v1 + v2);
	}
	Add(Expr *e1, Expr *e2) :Expr2(e1, e2) {}
};
// subtracts two expressions
class Sub : public Expr2 {
public:
	long eval() override {
		long v1 = e1->eval();
		long v2 = e2->eval();
		Log::log_msg(std::to_string(v1) + "-" + std::to_string(v2) + "=" + std::to_string(v1-v2), Log::Level::eval);
		return (v1-v2);
	}
	Sub(Expr *e1, Expr *e2) :Expr2(e1, e2) {}
};
// wrapper for a single value. eval() simply returns the value.
class Num : public Expr {
public:
	long val;
//
	long eval() override {
		Log::log_msg("Passing " + std::to_string(val), Log::Level::eval);
		return val;
	}
	Num(long value) {
		val = value;
	}
};
// stores a token recognized by the parser
class Tok {
public:
	enum Type 
	{
		null, lparen, rparen, plus, minus, times, div, dice, high, number
	};
	Type t;
	int val; //I should probably have made a subclass for numeric tokens, but I didn't

	static std::string to_str(Tok::Type st) {
		if (st == Type::null) {
			return "NULL";
		} else if (st == Type::lparen) {
			return "(";
		} else if (st == Type::rparen) {
			return ")";
		} else if (st == Type::plus) {
			return "+";
		} else if (st == Type::minus) {
			return "-";
		} else if (st == Type::times) {
			return "*";
		} else if (st == Type::div) {
			return "/";
		} else if (st == Type::dice) {
			return "d";
		} else if (st == Type::high) {
			return "h";
		} else if (st == Type::number) {
			return "number";
		} else {
			return NULL;
		}
	}
//
	Tok(Type type, int value) {
		t = type;
		val = value;
	}
	Tok(Type type) {
		t = type;
		val = 0;
	}
};
//
/* headers to all the parse functions. since they are recursive they must be able to
call each other in any order. It would have been better to put this in a header file but I still
don't really know how to use Visual Studio so here they are for now. */
//
Expr *parse_roll(std::list<Tok*>::iterator *begin, std::list<Tok*>::iterator *end);
Expr *parse_add_sub(std::list<Tok*>::iterator *begin, std::list<Tok*>::iterator *end);
Expr *parse_mul_div(std::list<Tok*>::iterator *begin, std::list<Tok*>::iterator *end);
//
//the tokenizer: turns an input string into a parser-compatible list of Toks
std::list<Tok*>* tokenize_input(const std::string& input) {
	std::regex match_d("^d");
	std::regex match_h("^h");
	std::regex match_num("^[0-9]+");
	std::regex match_lparen("^\\(");
	std::regex match_rparen("^\\)");
	std::regex match_plus("^\\+");
	std::regex match_minus("^\\-");
	std::regex match_star("^\\*");
	std::regex match_slash("^/");
	//
	std::list<Tok*> *toks = new std::list<Tok*>();
	std::smatch *res = new std::smatch();
	//
	size_t i{ 0 };
	while (i < input.size()) {
		if (std::regex_search(input.begin() + i, input.end(), match_d)) {
			toks->push_back(new Tok(Tok::Type::dice));
			Log::log_msg("d", Log::Level::tokenizer);
			i++;
		}
		else if (std::regex_search(input.begin() + i, input.end(), match_h)) {
			toks->push_back(new Tok(Tok::Type::high));
			Log::log_msg("h", Log::Level::tokenizer);
			i++;
		}
		else if (std::regex_search(input.begin() + i, input.end(), match_lparen)) {
			toks->push_back(new Tok(Tok::Type::lparen));
			Log::log_msg("(", Log::Level::tokenizer);
			i++;
		}
		else if (std::regex_search(input.begin() + i, input.end(), match_rparen)) {
			toks->push_back(new Tok(Tok::Type::rparen));
			Log::log_msg(")", Log::Level::tokenizer);
			i++;
		}
		else if (std::regex_search(input.begin() + i, input.end(), match_plus)) {
			toks->push_back(new Tok(Tok::Type::plus));
			Log::log_msg("+", Log::Level::tokenizer);
			i++;
		}
		else if (std::regex_search(input.begin() + i, input.end(), match_minus)) {
			toks->push_back(new Tok(Tok::Type::minus));
			Log::log_msg("-", Log::Level::tokenizer);
			i++;
		}
		else if (std::regex_search(input.begin() + i, input.end(), match_star)) {
			toks->push_back(new Tok(Tok::Type::times));
			Log::log_msg("*", Log::Level::tokenizer);
			i++;
		}
		else if (std::regex_search(input.begin() + i, input.end(), match_slash)) {
			toks->push_back(new Tok(Tok::Type::div));
			Log::log_msg("/", Log::Level::tokenizer);
			i++;
		}
		else if (std::regex_search(input.begin() + i, input.end(), *res, match_num)) {
			std::string num_str = res->str();
			int val = stoi(num_str);
			toks->push_back(new Tok(Tok::Type::number, val));
			Log::log_msg(num_str, Log::Level::tokenizer);
			i += num_str.size();
		}
		else {
			Log::log_msg("Unknown token at index: " + std::to_string(i), Log::Level::error);
			return NULL;
		}
	}
	//
	delete(res);
	//
	return toks;
}
//
/* 
parser CFG:
AS --> MD | AS + MD
MD --> R | MD * R
R  --> (AS) | n | ndm | ndmhk
//
where d, h are tokens and n, m, k are integers
*/
//
//gets the next token for the parser
Tok::Type peek(std::list<Tok*>::iterator *begin, std::list<Tok*>::iterator *end) {
	if (*begin == *end) {
		return Tok::Type::null;
	}
	return (**begin)->t;
}
//
//advances the parser's iterator if it's safe to do so.
void consume(std::list<Tok*>::iterator *begin, std::list<Tok*>::iterator *end) {
	if (*begin != *end) {
		Log::log_msg("Consumed " + Tok::to_str(peek(begin, end)), Log::Level::parser);
		(*begin)++;
	}
}
//
//despite the name, this function can parse either a dice roll, a number or a set of parentheses.
Expr * parse_roll(std::list<Tok*>::iterator *begin, std::list<Tok*>::iterator *end) {
	if (peek(begin, end) == Tok::Type::rparen) {
		consume(begin, end);
		Log::log_msg("Parsing parenthetical", Log::Level::parser);
		Expr *p = parse_add_sub(begin, end);
		if (peek(begin, end) == Tok::Type::lparen) {
			consume(begin, end);
			return p;
		}
		else {
			Log::log_msg("Unmatched parentheses", Log::Level::error);
			return NULL;
		}
	}
	if (peek(begin, end) == Tok::Type::number) {
		int v1 = (**begin)->val;
		int v2{ 0 };
		consume(begin, end);
		if (peek(begin, end) == Tok::Type::high) {
			int v3{ 0 };
			consume(begin, end);
			if (peek(begin, end) == Tok::Type::number) {
				v2 = (**begin)->val;
			}
			else {
				Log::log_msg("Malformed roll", Log::Level::error);
				return NULL;
			}
			consume(begin, end);
			if (peek(begin, end) == Tok::Type::dice) {
				consume(begin, end);
				if (peek(begin, end) == Tok::Type::number) {
					v3 = (**begin)->val;
				}
				else {
					Log::log_msg("Malformed roll", Log::Level::error);
					return NULL;
				}
				consume(begin, end);
			}
			else {
				Log::log_msg("Malformed roll", Log::Level::error);
				return NULL;
			}
			Log::log_msg("Roll(" + std::to_string(v3) + "," + std::to_string(v2) + "," + std::to_string(v1) + ")", Log::Level::parser);
			return new Roll(v3, v2, v1);
		}
		else if (peek(begin, end) == Tok::Type::dice) {
			consume(begin, end);
			if (peek(begin, end) == Tok::Type::number) {
				v2 = (**begin)->val;
				Log::log_msg("Roll(" + std::to_string(v2) + "," + std::to_string(v1) + ")", Log::Level::parser);
				consume(begin, end);
				return new Roll(v2, v1, 0);
			}
			else {
				Log::log_msg("Malformed roll", Log::Level::error);
				return NULL;
			}
		} else {
			Log::log_msg("Num(" + std::to_string(v1) + ")", Log::Level::parser);
			return new Num(v1);
		}
	}
	else {
		Log::log_msg("Expected number or parenthesis", Log::Level::error);
		return NULL;
	}
}
//
//parses add or subtract, passes the first operand to mul/div and the second (if applicable) to itself
Expr * parse_add_sub(std::list<Tok*>::iterator *begin, std::list<Tok*>::iterator *end) {
	Log::log_msg("{", Log::Level::parser);
	Log::indent();
	Expr *e = parse_mul_div(begin, end);
	if (peek(begin, end) == Tok::Type::plus) {
		consume(begin, end);
		Log::log_msg("plus", Log::Level::parser);
		Expr *e2 = parse_add_sub(begin, end);
		Log::unindent();
		Log::log_msg("}", Log::Level::parser);
		return new Add(e2, e);
	}
	if (peek(begin, end) == Tok::Type::minus) {
		consume(begin, end);
		Log::log_msg("minus", Log::Level::parser);
		Expr *e2 = parse_add_sub(begin, end);
		Log::unindent();
		Log::log_msg("}", Log::Level::parser);
		return new Sub(e2, e);
	}
	Log::unindent();
	Log::log_msg("}", Log::Level::parser);
	return e;
}
//
//parses multiplication and division, passes first operand to parse_roll and second (if applicable) to itself
Expr * parse_mul_div(std::list<Tok*>::iterator *begin, std::list<Tok*>::iterator *end) {
	Log::log_msg("{", Log::Level::parser);
	Log::indent();
	Expr *e = parse_roll(begin, end);
	if (peek(begin, end) == Tok::Type::times) {
		consume(begin, end);
		Log::log_msg("times", Log::Level::parser);
		Expr *e2 = parse_mul_div(begin, end);
		Log::unindent();
		Log::log_msg("}", Log::Level::parser);
		return new Mul(e2, e);
	}
	if (peek(begin, end) == Tok::Type::div) {
		consume(begin, end);
		Log::log_msg("divided by", Log::Level::parser);
		Expr *e2 = parse_mul_div(begin, end);
		Log::unindent();
		Log::log_msg("}", Log::Level::parser);
		return new Div(e2, e);
	}
	Log::unindent();
	Log::log_msg("}", Log::Level::parser);
	return e;
}
//
void process_input(std::string input) {
	std::list<Tok*> *tokens = tokenize_input(input);
	if (tokens) {
		tokens->reverse();
		std::list<Tok*>::iterator begin = tokens->begin();
		std::list<Tok*>::iterator end = tokens->end();
		Expr *top_expr = parse_add_sub(&begin, &end);
		if (top_expr) {
			long result = top_expr->eval();
			delete(tokens);
			delete(top_expr);
//
			std::cout << result << '\n';
		}
	}
}
//
int main(int argc, char** argv) {
	Log::set_level(Log::Level::error);
//
	std::string input{ "" };
//
	if (argc > 3) {
		Log::log_msg("Too many arguments!", Log::Level::error);
		return 1;
	}
//
	if (argc == 3) {
		srand(atoi(argv[1]));
		input = argv[2];
		process_input(input);
		return 0;
	}
	else {
		using namespace std::chrono;
		milliseconds ms = duration_cast<std::chrono::milliseconds>(steady_clock::now().time_since_epoch());
		srand(ms.count());
	}
//
	if (argc == 2) {
		input = argv[1];
		process_input(input);
		return 0;
	}
//
	while (true) {
		std::cout << "> ";
		std::cin >> input;
		if (input == "exit") {
			return 0;
		}
		else {
			process_input(input);
		}
	}
}
