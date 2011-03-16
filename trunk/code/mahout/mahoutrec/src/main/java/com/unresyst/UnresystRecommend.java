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
import org.apache.mahout.common.FileLineIterable;
import org.apache.mahout.common.IOUtils;

public class UnresystRecommend {
    
    public static void main(String[] args) throws FileNotFoundException, TasteException, IOException, OptionException {

        // parameters: train data filename, number of recommendations per user , output filename        
        String trainFilename = args[0];     
        int recCount = Integer.parseInt(args[1]);
        String outputFilename = args[2];
        
        // create data source (model) - from the train csv file            
        File ratingsFile = new File(trainFilename);                        
        DataModel model = new FileDataModel(ratingsFile);                
        
        // create a simple recommender on our data
        CachingRecommender cachingRecommender = new CachingRecommender(new SlopeOneRecommender(model));
        
        // create recommendations for all users and write them to the output file
        //
        
        // open the file to write to
        File resultFile = new File(outputFilename);
        PrintWriter writer = new PrintWriter(new OutputStreamWriter(new FileOutputStream(resultFile), Charset.forName("UTF-8")));
        
        // for all users
        for (LongPrimitiveIterator it = model.getUserIDs(); it.hasNext();){
            long userId = it.nextLong();
            
            // get the recommendations for the user
            List<RecommendedItem> recommendations = cachingRecommender.recommend(userId, recCount);            
            
                            
            // print the list of recommendations for each recommendation
            for (RecommendedItem recommendedItem : recommendations) {

                long itemId = recommendedItem.getItemID();
                float prediction = recommendedItem.getValue();
                
                writer.println(String.format("%d,%d,%f", userId, itemId, prediction));
            }
        }
                        
        // writer spam
        writer.flush();
        IOUtils.quietClose(writer);                                
    }
}
