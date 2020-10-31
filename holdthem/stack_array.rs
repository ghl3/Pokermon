pub enum StackArray<T> {
    Zero,
    One(T),
    Two(T, T),
    Three(T, T, T),
    Four(T, T, T, T),
    Five(T, T, T, T, T),
    Overflow,
}

impl<T> StackArray<T> {
    pub fn push(self, t: T) -> StackArray<T> {
        match self {
            StackArray::Zero => StackArray::One(t),
            StackArray::One(a) => StackArray::Two(a, t),
            StackArray::Two(a, b) => StackArray::Three(a, b, t),
            StackArray::Three(a, b, c) => StackArray::Four(a, b, c, t),
            StackArray::Four(a, b, c, d) => StackArray::Five(a, b, c, d, t),
            StackArray::Five(..) => StackArray::Overflow,
            StackArray::Overflow => StackArray::Overflow,
        }
    }

    pub fn len(&self) -> usize {
        match self {
            StackArray::Zero => 0,
            StackArray::One(..) => 1,
            StackArray::Two(..) => 2,
            StackArray::Three(..) => 3,
            StackArray::Four(..) => 4,
            StackArray::Five(..) => 5,
            StackArray::Overflow => 6,
        }
    }
}
