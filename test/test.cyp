// cyprus example

[env
  (1
    (2
      (3
        exists~   a c
        reaction~   a :: a b
        reaction~   a :: b $
        reaction~   c :: c c
      )
      
      reaction~         b :: d
      reaction~         d :: d e
      reaction as c1~ c c :: c
      reaction as c2~   c :: $
      priority~        c1 >> c2 // c1 must be maximally applied before c2
    )
    
    reaction~ e :: !e
  )
]

// !sym = pass sym through containing membrane
// !sym!!container = pas sym out of containing membrane and into container
// $ = dissolve containing membrane
// $container = dissolve container's membrand

// on dissolution, rules disappear, but nested membranes stay as do particles

// particle definitions:
// exists~  a b = a and b exist without a charge as particles
// exists~ a+ b- = a exists as a particle and is positively charged,, etc.
// exists~ *a+ b = a exists as a positively charged catalyst (not consumed)

// keywords:
// [somename someparams ... ] = environment
// (somename someparams ... ) = membrane
// exists~ = particles that exist in the containing membrane
// reaction~ = a rule
// priority~ = assign a weight or a relationship between rules
//   eg. priority~ c1 >> c2 (c1 maximally chosen over c2)
// reaction as somename~ = assign a name to a reaction (for use in priority definitions)

// for the most part, whitespace doesn't matter, except that newlines
// determine when a statement ends, and spaces separate tokens
