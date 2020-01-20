
#define NUMQPs 8

void f()
{
  int element, qp, numElements = 100, NUMQPs = 8;
  int *data_in[NUMQPs];

  # pragma omp target data map (...)
  # pragma omp teams num_teams (...) num_threads (...) private (...)
  # pragma omp distribute
  for ( element = 0; element < numElements ; ++ element ) {
  int total = 0;
  # pragma omp parallel for
  for (qp = 0; qp < numQPs ; ++ qp)
  total += dot ( left [ element ][ qp], right [ element ][ qp ]);
  elementValues [ element ] = total ;
  }
  //Option 2: OpenACC
  # pragma acc parallel copy (...) num_gangs (...) vector_length (...)
  # pragma acc loop gang vector
  for ( element = 0; element < numElements ; ++ element ) {
  total = 0;
  for (qp = 0; qp < numQPs ; ++ qp)
  total += dot ( left [ element ][ qp], right [ element ][ qp ]);
  elementValues

  //Option 2: OpenCL
  # pragma acc parallel copy (...) num_gangs (...) vector_length (...)
  # pragma acc loop gang vector
  for ( element = 0; element < numElements ; ++ element ) {
  total = 0;
  for (qp = 0; qp < numQPs ; ++ qp)
  total += dot ( left [ element ][ qp], right [ element ][ qp ]);
  elementValues

}