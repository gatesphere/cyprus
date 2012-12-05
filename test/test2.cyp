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
[env2
  (12
    (22
      (32
        exists~   a c
        reaction~   a :: a b
        reaction~   a :: b $
        reaction~   c :: c c
      )
      
      reaction~          b :: d
      reaction~          d :: d e
      reaction as c12~ c c :: c
      reaction as c22~   c :: $
      priority~        c12 >> c22 // c12 must be maximally applied before c22
    )
    
    reaction~ e :: !e
  )
]
