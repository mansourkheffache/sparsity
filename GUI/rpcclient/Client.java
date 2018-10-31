package rpcclient;


import org.apache.xmlrpc.client.*;

import javax.swing.*;
import java.io.FileOutputStream;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;


public class Client {

    public String nodeEndpoint=""; // getText()
    public static final String fakeOriginAddress = "ffffffffffffffff"; // hardcoded leave it as it is!
    public static ArrayList<Integer> generatedData;
    public static int X;
    public JTextPane infoAreaPane;
    String outputFileName = "output.txt";
    String requestedVector = "vector.txt";
    int dataHammingDistance;

    public Client(JTextPane infoAreaPane){
        infoAreaPane = infoAreaPane;
    }


    public void init(String nodeNetworkAddress)
    {


        // Getting Dimensionality of X data
        // int n = 32; // Dimensionality of the Data (Fancy Word: Hyperdimensional Vector) we will retrieve it from the nodes!
        nodeEndpoint = nodeNetworkAddress;
        // Connecting to Node
        X = connectToNode();  //Dimensionality of the Data (Fancy Word: Hyperdimensional Vector) we will retrieve it from the nodes!


    }


    public String generateAndStore(int numberOfVectors)
    {
        StringBuilder sb = new StringBuilder();
        for(int i=0;i<numberOfVectors;i++)
        {
            List dataToStore = generateData(X);
            Integer storageLocations = storeData(dataToStore);
            System.out.println(storageLocations);
            ArrayList<Integer> data = (ArrayList<Integer>) dataToStore;
            // function to append on file!
            writeToFile(outputFileName,data);
            sb.append(" Vector "  + i + " stored in " + storageLocations.toString()  + " different storage locations!. \n ");
        }

        return sb.toString();

    }


    public List generateData(int n)
    {
        ArrayList<Integer> list = new ArrayList<>();
        Random random = new Random();

        for (int i = 0; i < n; i++)
        {
            list.add(random.nextInt(2));
        }
        List dataToStore = (List) list ;
        return dataToStore;
    }


    public Integer storeData(List dataToStore)
    {
        Integer count=null;
        try
        {
            XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
            config.setServerURL(new URL(nodeEndpoint));
            XmlRpcClient client = new XmlRpcClient();
            client.setConfig(config);
            Object[] params = new Object[]{ dataToStore, fakeOriginAddress};
            Object rawResponse = (Object) client.execute("store", params);
            count = (Integer) rawResponse;
        }
        catch(Exception e)
        {
            System.out.println(e.toString());
        }

        return count;
    }

    public int connectToNode()
    {
        Integer widthData = null;
        try
        {

            XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
            config.setServerURL(new URL(nodeEndpoint));
            XmlRpcClient client = new XmlRpcClient();
            client.setConfig(config);
            Object[] paramsEmpty = new Object[]{};
            Object rawResponse = (Object) client.execute("connect", paramsEmpty);
            widthData = (Integer) rawResponse;
        }
        catch(Exception e)
        {
            System.out.println(e.toString());
        }
        return widthData;
    }

    public Integer[] retrieveData(List data)
    {
        Integer[] result = null;
        try
        {

            XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
            config.setServerURL(new URL(nodeEndpoint));
            XmlRpcClient client = new XmlRpcClient();
            client.setConfig(config);
            Object[] params = new Object[]{data, fakeOriginAddress};
            Object[] rawResponse = (Object[]) client.execute("retrieve", params);
            result = Arrays.asList(rawResponse).toArray(new Integer[0]);
        }
        catch(Exception e)
        {
            System.out.println(e.toString());
        }

        return result;
    }

    public  ArrayList<Integer> binarizeData(Integer[] retrievedValue)
    {

        ArrayList<Integer> binarizedData = new ArrayList<>();
        for (int i = 0; i < retrievedValue.length; i++)
        {
            if(retrievedValue[i]>=0)
                binarizedData.add(1);
            if(retrievedValue[i] < 0)
                binarizedData.add(0);
        }
        return binarizedData;
    }


    public int dataComparison(ArrayList<Integer> binarizedData, ArrayList<Integer> dataToStore )
    {
        int hammingDistance = 0;
        for(int i = 0;i < binarizedData.size();i++)
        {
            if(!binarizedData.get(i).equals(dataToStore.get(i)))
            {
                hammingDistance++;
            }
        }
        return hammingDistance;

    }

    public String searchAndBrush(ArrayList<Integer> currentData)
    {
        StringBuilder sb = new StringBuilder();
        //int dataHammingDistance;
        boolean foundVector = false;
        int numberOfIterations=1;
        ArrayList<Integer>  previousBinaryData;
        boolean isSearching =true;
        ArrayList<Integer> currentBinaryData = new ArrayList<Integer>(currentData);
        while(isSearching)
        {
            System.out.println("Current Iteration " + numberOfIterations);
            List currentInputData = (List) currentBinaryData;

            /*
            Integer currentStorageLocations =  storeData(currentInputData);
            System.out.println("Data was stored in  " + currentStorageLocations + " locations.");
            */
            Integer[] currentRetrievedData = retrieveData(currentInputData);
            System.out.println("Noisy data equals to: " );
            for(int i = 0; i < currentRetrievedData.length; i++)
            {
                System.out.print(currentRetrievedData[i]);
                System.out.print(" ");
            }
            System.out.println("");
            System.out.println("Binarized Data equals to: ");


            previousBinaryData  = new ArrayList<Integer>(currentBinaryData);
            currentBinaryData = binarizeData(currentRetrievedData);

            for(int i = 0; i < currentBinaryData.size(); i++)
            {
                System.out.print(currentBinaryData.get(i));
            }



            int currentHammingDistance = dataComparison(currentBinaryData, previousBinaryData);

            System.out.println("");
            System.out.println("Current Hamming Distance is : " + currentHammingDistance);
            System.out.println("");

            if(currentHammingDistance == 0 )
            {
                foundVector = true;
                System.out.println("Voilà! Here is the clean version of the data you requested! " );
                for(int i = 0; i < currentBinaryData.size(); i++)
                {
                    System.out.print(currentBinaryData.get(i));
                }
                System.out.println(" \n Original Data:");
                for(int i = 0; i < currentData.size(); i++)
                {
                    System.out.print(currentData.get(i));
                }
                dataHammingDistance = dataComparison(currentData,currentBinaryData);
                System.out.println(" \n Hamming distance between retrieved data and original one : " + dataHammingDistance);
                break;
            }
            if( numberOfIterations > 15 && currentHammingDistance >= X/2)
            {
                System.out.println("We couldn't find the data you requested! Désolè! Hamming Distance diverges to : " + currentHammingDistance);
                isSearching = false;
                break;
            }
            numberOfIterations++;
        }

        writeToFile(requestedVector,currentBinaryData);
        if(foundVector)
        {

            sb.append("We were able to find your data! with a Hamming Distance of : " );
            sb.append(dataHammingDistance);
        }
        if(!foundVector)
        {
            sb.append("We couldn't find your data! The search query diverged!");
        }
        return sb.toString();
    }

    public ArrayList<Integer> string2ArrayList(String s)
    {
        ArrayList<Integer> result = new ArrayList<Integer>();
        // Splits each spaced integer into a String array.
        String[] integerStrings = s.split(" ");
        for (int i = 0; i < integerStrings.length; i++)
        {
            result.add(Integer.parseInt(integerStrings[i]));
        }
        return result;
    }

    public String arrayList2String (ArrayList<Integer> inp)
    {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < inp.size(); i++) {
            sb.append(inp.get(i));
            sb.append(" ");
        }
        //sb.deleteCharAt(sb.length() - 1);
        sb.append("\r\n");

        return sb.toString();
    }

    public void writeToFile (String fileName, ArrayList<Integer> dataToStore)
    {
        String dataString = arrayList2String(dataToStore);

        try
        {
            FileOutputStream out = new FileOutputStream(fileName, true);
            out.write(dataString.getBytes());
            out.close();
            System.out.println("success in writing output to file");
        }
        catch (Exception e)
        {
            System.out.println(e);
        }
    }
}





