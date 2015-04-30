#fuzzylogic
fuzzylogic v2 - May 2015
use of fuzzy logic to very accurately predict what a user is looking for

fuzzylogic is light, fast, and easy to use. 
I will do a proper writeup of how to use it soon, but for now I recommend the following usage:

`
fuzzylogic.extractOne('query', list_of_choices, score_cutoff=25)[0]
`

*extractOne() returns a tuple with the result and the score*

**query** *is the lookup string*

**choices** *is a list with all the possible choices*

**score_cutoff** *is a percentage match (I would recommend keeping this at 25% or higher)*
