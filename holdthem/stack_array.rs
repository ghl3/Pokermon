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
            StackArray::Five(a, b, c, d, e) => StackArray::Overflow,
            StackArray::Overflow => StackArray::Overflow,
        }
    }

    pub fn len(&self) -> usize {
        match self {
            StackArray::Zero => 0,
            StackArray::One(a) => 1,
            StackArray::Two(a, b) => 2,
            StackArray::Three(a, b, c) => 3,
            StackArray::Four(a, b, c, d) => 4,
            StackArray::Five(a, b, c, d, e) => 5,
            StackArray::Overflow => 6,
        }
    }
}
