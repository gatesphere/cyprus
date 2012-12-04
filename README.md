cyprus
======

A membrane-computing oriented programming language

Overview
--------
Cyprus is a programming language based on the concept of a [P System](http://en.wikipedia.org/wiki/P_system).
Computation is modeled as chemical reactions happening within protocellular
constructions, producing new chemicals.

License
-------
Cyprus is [BSD Licensed](https://raw.github.com/gatesphere/cyprus/master/license/license.txt).

Terminology
-----------
Cyprus uses several unique terms when it comes to programming languages.
These are described below.

Container - an object that holds membranes, particles, and reaction definitons.

Environment - a container that cannot be dissolved, nor whose walls can
be permeated.  A Cyprus program consists of at least one, possibly many,
environment definitions.

Membrane - a container nested within an environment or another membrane.
Membranes can be dissolved and their walls can be permeated.

Particle - a chemical, required for reactions to take place, and produced
by reactions.

Reaction - a rule governing the interaction of particles within a membrane.

Priority - an ordering of reactions.  Reactions with a higher priority
will be maximally applied before those with a lower priority.

How Cyprus Works
----------------
Cyprus is governed by a single monolithic clock.  All activity within
all environments occurs in lockstep with the tick of the clock.  Each
tick, all reactions that are applicable within a given container are applied
maximally, obeying reaction priorities.  The clock stops ticking when no more
reaction applications can occur.  At this point, the particles contained by
the environments are interpreted as the final output of the program,
with everything else left in the system discarded as leftover state.

During the execution of a Cyprus program, membranes may dissolve, destroying
their reaction defenitions with them, but spilling their particles into
their parent container.  Environments cannot dissolve.

Particles may also osmose through their containing membrane's walls, either
targeting their container's parent, or a specific membrane by way of names.
Using named targets, a particle can osmose deeper into nested membranes,
or pass through multiple containing membranes.  Environments cannot be 
osmosed through, though particles may osmose over environmental boundaries.

Reaction application is maximal, but non-deterministic: reactions are 
applied in any valid order which obeys the assigned reaction priorities.

Cyprus is a Turing complete language, though using it for anything other
than fun and experimentation would be insane.  It is therefore an extremely
losely defined [Turing Tarpit](http://en.wikipedia.org/wiki/Turing_tarpit).

Getting Cyprus
--------------
Getting Cyprus is simple:

  1. Ensure you have Python 2.7 installed (not Python 3+!)
  2. Install funcparser lib with `pip install funcparserlib`
  3. Clone this repo
    
You've got a working Cyprus distribution now.

Using Cyprus
------------
Cyprus may be invoked like so:

    python cyprus.py
    
But this will give you errors:

    $ python cyprus.py
    usage: python cyprus.py [-p] <filename.cyp>
           python cyprus.py -v
           python cyprus.py -h
      -p: pretty-print a parse tree and exit
      -v: display version info and exit
      -h: display this help text and exit
      
I'm sure you can figure it out from here.

Cyprus' grammar
---------------
Here's the grammar, in a modified EBNF:

    program        := {env}
    env            := "[", body, "]"
    membrane       := "(", body, ")"
    body           := <name>, {statement}
    statement      := membrane | expr
    expr           := exists | reaction | priority
    exists         := "exists", "~", name, {name}
    reaction       := "reaction", <"as", name>, "~", name, {name}, "::",
                       {symbol} 
    priority       := "priority", "~", name, ">>", name
    name           := number | atom
    atom           := [A-Za-z], {[A-Za-z0-9]}
    number         := [0-9], {[0-9]} | {[0-9]}, ".", [0-9], {[0-9]}
    symbol         := atom | "!", name, <"!!", name> | "$", [name]


Example programs
----------------
Here's an annotated example program, (test/test.cyp) that generates 
perfect squares:

    // generate perfect squares
    // comments are defined with // to the end of the line
    [env       // open an environment, call it "env"
      (1       // open a membrane, call it "1"
        (2     // open a membrane, call it "2"
          (3   // open a membrane, call it "3"
            // seed the membrane "3" with 2 particles, "a" and "c"
            exists~   a c
            
            // define some reactions (in "3")
            reaction~   a :: a b  // take an "a", produce "a" and "b"
            reaction~   a :: b $  // take an "a", produce "b" and dissolve self
                                  // reaction~ a :: b $3 would do the same in
                                  //                     this situation.
                                  // reaction~ a :: b $foo would dissolve
                                  //                       container "foo" 
            reaction~   c :: c c  // take a "c", produce two "c"s
          )
          
          // define some reactions (in "2")
          reaction~         b :: d
          reaction~         d :: d e
          reaction as c1~ c c :: c  // name this reaction c1
          reaction as c2~   c :: $  // name this reaction c2
          
          // define rule priority
          priority~        c1 >> c2 // c1 must be maximally applied before c2
          // named reactions are required for rule priorities
        )
        
        // define a reaction (in "3")
        reaction~ e :: !e // take an "e", osmose an "e" to parent container
                          // reaction~ e :: !e!!env would do the same in this
                          //                        situation.
                          // reaction~ e :: !e!!foo would make "e" osmose to
                          //                        container "foo"
      )
    ]

The output here is the amount of "e" particles in the environment at the
end of the program's execution.

Here's another example annotated program (test/hello.cyp), that produces 
a "hello, world!" effect:

    // hello world in cyprus

    [ // names are optional
      (
        exists~ hello
        reaction~ hello :: hello world $
      )
    ]

Those examples, along with the grammar, show pretty much all you need to 
know about writing Cyprus programs.

Planned features
----------------
  - Proper runtime errors
  - Proper parsing errors
  - Particle and membrane charges
  - Variable membrane permeability
  - Syntactic sugar for catalysts (`reaction~ *x :: x` == `reaction~ x :: x x`)
  - Better output
  - More commandline flags (-verbose, etc.)
  - Clean up code (remove globals, comment, etc.)
