package com.unresyst;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.List;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.OutputStreamWriter;
import java.io.FileOutputStream;
import java.nio.charset.Charset;

import org.apache.commons.cli2.OptionException; 
import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.recommender.CachingRecommender;
import org.apache.mahout.cf.taste.impl.recommender.slopeone.SlopeOneRecommender;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.impl.common.LongPrimitiveIterator;
import org.apache.mahout.cf.taste.common.NoSuchUserException;
import org.apache.mahout.cf.taste.common.NoSuchItemException;
import org.apache.mahout.common.FileLineIterable;
import org.apache.mahout.common.IOUtils;

public class UnresystPredict {
    
    public static void main(String[] args) throws FileNotFoundException, TasteException, IOException, OptionException {
        // parameters: train data filename, test data filename, output filename
        
        String trainFilename = args[0];     
        String testFilename = args[1];
        String outputFilename = args[2];
        
        // create data source (model) - from the train csv file            
        File ratingsFile = new File(trainFilename);                        
        DataModel model = new FileDataModel(ratingsFile);                
        
        // create a simple recommender on our data
        CachingRecommender cachingRecommender = new CachingRecommender(new SlopeOneRecommender(model));
        
        // open the test csv file
        File testFile = new File(testFilename);
        
        // predict for all test pairs and write it to the output file
        //
        
        // open the file to write to
        File resultFile = new File(outputFilename);
        PrintWriter writer = new PrintWriter(new OutputStreamWriter(new FileOutputStream(resultFile), Charset.forName("UTF-8")));
        
        // iterate through the test pairs
        for (String line : new FileLineIterable(testFile, true)){
            
            // parse the userId and itemId
            String[] parsedLine = line.split(",");            
            long userId = Long.parseLong(parsedLine[0]);
            long itemId = Long.parseLong(parsedLine[1]);
            
            float prediction;
            try{
                // get the prediction
                prediction = cachingRecommender.estimatePreference(userId, itemId);
            }catch (NoSuchUserException e){
                prediction = new Float(0.5);
            }
            catch (NoSuchItemException e){
                prediction = new Float(0.5);
            }

            // if it doesn't exist, replace it by 0.5
            if (Float.isNaN(prediction)){
                prediction = new Float(0.5);
            }
            // print it to the output file
            writer.println(String.format("%d,%d,%f", userId, itemId, prediction));
            
            
        }
        // writer spam
        writer.flush();
        IOUtils.quietClose(writer);                
                
    }
}
