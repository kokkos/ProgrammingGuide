#Select paralliziation:
#DEVICES={"OpenACC"; "OpenMP"; "Serial"; "KokkosCuda"; "OpenCL"}
DEVICES = "OpenACC"
//DEVICES = "Kokkos"

KOKKOS_PATH = ${HOME}/Kokkos/kokkos

EXE_NAME = matvec
SRC_DIR = src
OBJ_DIR = obj

default: build
	echo "Start Build"

#Kokkos (CUDA)
ifneq (,$(findstring Kokkos,$(DEVICES)))
CXX = ${KOKKOS_PATH}/bin/nvcc_wrapper
EXE = ${EXE_NAME}_kokkos
KOKKOS_ARCH = "Volta70"
KOKKOS_CUDA_OPTIONS = "enable_lambda"
KOKKOS_DEVICES="Cuda"

#OpenMP
else ifneq (,$(findstring OpenMP,$(DEVICES)))
CXX = g++
CXXFLAGS = -fopenmp 
EXE = ${EXE_NAME}_openmp
KOKKOS_DEVICES="OpenMP"
KOKKOS_ARCH = "None"
KOKKOS_CPP_DEPENDS = 
KOKKOS_LINK_DEPENDS = 
KOKKOS_LIBS =

#OpenACC
else ifneq (,$(findstring OpenACC,$(DEVICES)))
CXX = pgc++
KOKKOS_CXXFLAGS = 
CXXFLAGS = -ta=tesla
EXE = ${EXE_NAME}_openacc
KOKKOS_ARCH = "None"
KOKKOS_CPP_DEPENDS = 
KOKKOS_LINK_DEPENDS = 
LINKFLAGS = -acc
KOKKOS_LIBS =

#Sserial
else
CXX = g++
EXE = ${EXE_NAME}_serial
KOKKOS_ARCH = "None"
KOKKOS_CPP_DEPENDS = 
KOKKOS_LINK_DEPENDS = 
KOKKOS_LIBS =
endif

CXXFLAGS += -O3
LINK += ${CXX}
LINKFLAGS +=
DEPFLAGS += -M

SRC_ALL = $(wildcard $(SRC_DIR)/*.cpp)
SRC = $(filter-out $(wildcard $(SRC_DIR)/matvec_*.cpp), $(SRC_ALL))
SRC += $(SRC_DIR)/$(EXE).cpp 
OBJ = $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SRC))

#Including Kokkos headers as Kokkos::timer used in all implementations
include $(KOKKOS_PATH)/Makefile.kokkos

build: print $(EXE) 

print:
	echo $(SRC)

$(EXE): $(OBJ) $(KOKKOS_LINK_DEPENDS)
	$(LINK) $(KOKKOS_LDFLAGS) $(LINKFLAGS) $(EXTRA_PATH) $(OBJ) $(KOKKOS_LIBS) $(LIB) -o $(EXE)

clean: kokkos-clean
	rm -f *.o *.cuda matvec_* *.host ${EXE} $(OBJ_DIR)/*

# Compilation rules

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp $(KOKKOS_CPP_DEPENDS)
	$(CXX) $(KOKKOS_CPPFLAGS) $(KOKKOS_CXXFLAGS) $(CXXFLAGS) $(EXTRA_INC) -c $< -o $@

test: $(EXE)
	./$(EXE)
