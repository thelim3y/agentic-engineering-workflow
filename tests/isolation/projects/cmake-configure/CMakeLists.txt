cmake_minimum_required(VERSION 3.16)
project(isolation_probe LANGUAGES CXX)

if(PROBE_MODE STREQUAL "attack")
  file(WRITE "$ENV{ISO_PROT}/CTestTestfile.cmake"
    "add_test(NAME nothing COMMAND true)\n")
elseif(PROBE_MODE STREQUAL "positive")
  add_executable(allowed main.cpp)
else()
  message(FATAL_ERROR "Unknown probe mode")
endif()
