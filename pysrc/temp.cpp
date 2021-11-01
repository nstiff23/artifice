//despite the name, this function parses either a roll, a number or a set of parentheses.
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
		}
		else {
			Log::log_msg("Num(" + std::to_string(v1) + ")", Log::Level::parser);
			return new Num(v1);
		}
	}
	else {
		Log::log_msg("Expected number or parenthesis", Log::Level::error);
		return NULL;
	}
}

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