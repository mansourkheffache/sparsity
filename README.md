# sparsity
Distributed sparse distributed memory for Network Programming @ LTU Sweden

(Python 3.6.6)

## How to run

(1) First start the tracker script, default port is set to 8000   
```
python3 tracker.py S X N T C
```
Params:   
  S:  ID space for peers   
  X:  width of data/addresses   
  N:  peer storage capacity   
  T:  address/data hamming distance threshold    
  C:  ceiling for storage bins values  
  
  
(2) Then you can either start a single node manually, or a nest (which automatically starts an N number of nodes - starting from port 5000 by default)   
```
python3 node.py TRACKER-ADDR:PORT

python3 nest.py N TRACKER-ADDR:PORT
```


  
