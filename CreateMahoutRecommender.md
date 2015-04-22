# Mahout for Newbies: How to Create a Recommender #
A short tutorial on actions you have to take to create your first Mahout recommender.

## Introduction ##

[Mahout](http://mahout.apache.org/) is a library containing scalable implementation of many machine learning algorithms, notably the collaborative filtering and other algorithms used in recommender systems.

There are many tutorials on creating simple or more complex recommenders but for Mahout newbies it's quite difficult to cope with all the technical details you have to do to make Mahout work in your way.

I'm not an Eclipse fan, so all instructions use only the shell console. I was running the examples on Ubuntu 10.04, but it should be working on most of the linux distros and even on windows with cygwin.

This page is aiming to be a step-by-step description for Mahout/Maven beginners. I'm also a Mahout/Maven beginner, so any corrections and comments are more then welcome.

## Part 1: Installation ##
There's a good [installation guide in the Mahout wiki](https://cwiki.apache.org/confluence/display/MAHOUT/BuildingMahout).

I'm running the 0.4 Mahout release, so all stuff in this article is primarily for that, but should be working also on trunk and other releases.

As described in the guide, after JDK and Maven you should do something like:
```
cd core
mvn compile
mvn install
```

A few things to note here:
  * If you installation fails, try the fix proposed in the tutorial:
```
rm -rf ~/.m2/
mvn clean install
```
  * If this doesn't help, try again
```
mvn  install
```
> > and look to the core/target/surefire-reports/. If you can find the cause of the problem there, you're a lucky person. If not, you can seek help on the `user@mahout.apache.org` mailing list as [I successfully  did.](http://comments.gmane.org/gmane.comp.apache.mahout.user/5881)
  * Alternatively, you can try running the install without tests
```
mvn -Dmaven.test.skip=true install
```

## Part 2: Creating a simple recommender ##

Now that you have mahout successfully installed, you can try some built-in examples, as [described in the Mahout wiki](https://cwiki.apache.org/confluence/display/MAHOUT/RecommendationExamples). Firstly you have to download some dataset, and then pass it as the `-i` parameter. It's a kind of a detective work but you can find some hints in the source code of the examples. I've successfully run the recommender on  [the Book Crossing dataset](http://www.informatik.uni-freiburg.de/~cziegler/BX/)

And now to creating your own recommender on your own data. Editing the examples isn't a good idea, because the code gets quite messy and all the paths are terribly long. Instead of that follow the oncoming steps.

### Create a Maven project ###
Firstly, you have to create a maven project. Go to the Mahout directory (the parent of the core directory) and run something like:
```
mvn archetype:create -DarchetypeGroupId=org.apache.maven.archetypes -DgroupId=com.unresyst -DartifactId=mahoutrec
```
This creates an empty project called `mahoutrec` with the package namespace `com.unresyst`. Now change to the `mahoutrec` directory. You can try out the new project by running:
```
mvn compile
mvn exec:java -Dexec.mainClass="com.unresyst.App"
```
This should print the Hello world message. If not try passing the `-e` option for the second command and try to realize what's going wrong.

More info on creating a Maven project can be found in [the official guide](http://maven.apache.org/guides/getting-started/)

### Set the project dependencies ###
Now that you have your maven project, let's set it up for your Mahout instalation.

Open the `pom.xml` file from your project directory (`mahoutrec`) in your favourite text editor. And now:
  * add the Mahout dependencies to your `pom.xml`. The following `<dependency>` elements must be under the `<dependencies>` parent element.
```
    <dependency>
      <groupId>org.apache.mahout</groupId>
      <artifactId>mahout-core</artifactId>
      <version>0.4</version>
    </dependency>
    <dependency>
      <groupId>org.apache.mahout</groupId>
      <artifactId>mahout-math</artifactId>
      <version>0.4</version>
    </dependency>
    <dependency>
      <groupId>org.apache.mahout</groupId>
      <artifactId>mahout-math</artifactId>
      <version>0.4</version>
      <type>test-jar</type>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.apache.mahout</groupId>
      <artifactId>mahout-utils</artifactId>
      <version>0.4</version>
    </dependency>
```

> If you are using other than the 0.4 version replace the 0.4 by the number of your version.
  * Set the relative path to the parent project `pom.xml` by adding the `<relativePath>` element to the `<parent>` element:
```
    <relativePath>../pom.xml</relativePath>    
```
Your whole `pom.xml` should look like that:
```
<?xml version="1.0"?>
<project xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd" xmlns="http://maven.apache.org/POM/4.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <artifactId>mahout</artifactId>
    <groupId>org.apache.mahout</groupId>
    <version>0.4</version>
    <relativePath>../pom.xml</relativePath>    
  </parent>
  <groupId>com.unresyst</groupId>
  <artifactId>mahoutrec</artifactId>
  <version>1.0-SNAPSHOT</version>
  <name>mahoutrec</name>
  <url>http://maven.apache.org</url>
  <dependencies>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>3.8.1</version>
      <scope>test</scope>
    </dependency>
     <dependency>
      <groupId>org.apache.mahout</groupId>
      <artifactId>mahout-core</artifactId>
      <version>0.4</version>
    </dependency>
    <dependency>
      <groupId>org.apache.mahout</groupId>
      <artifactId>mahout-math</artifactId>
      <version>0.4</version>
    </dependency>
    <dependency>
      <groupId>org.apache.mahout</groupId>
      <artifactId>mahout-math</artifactId>
      <version>0.4</version>
      <type>test-jar</type>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.apache.mahout</groupId>
      <artifactId>mahout-utils</artifactId>
      <version>0.4</version>
    </dependency>
  </dependencies>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
</project>
```

Now try compiling your project by running
```
mvn compile
```
You should get a Build successful message.

### Create a simple recommender ###
And now to the promised creation of your own recommender running on your own data. Firstly we'll create some dummy data to feed the recommender. Create a `datasets` directory in your project directory and create the `dummy-bool.csv` file with the following contents:
```
#userId,itemId
1,3
1,4
2,44
2,46
3,3
3,5
3,6
4,3
4,5
4,11
4,44
5,1
5,2
5,4
```
The first line is a comment, all the others are boolean preferences for items expressed by the users. Boolean preferences are useful when you don't have any explicit user-item ratings in your data. A boolean preference can mean e.g. that the user has viewed a profile page of the item. The example file states that the user id `1` has viewed the item id `3`, and item id `4`, user `2` item `44` and `46`, and so on.

Now, let's create the recommender. Create a file UnresystBoolRecommend.java in the well hidden subddirectory `src/main/java/com/unresyst/` of your project directory. Place the following content to the file
```
package com.unresyst;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.List;
import java.io.IOException;

import org.apache.commons.cli2.OptionException; 
import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.recommender.CachingRecommender;
import org.apache.mahout.cf.taste.impl.recommender.slopeone.SlopeOneRecommender;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.impl.common.LongPrimitiveIterator;

public class UnresystBoolRecommend {
    
    public static void main(String... args) throws FileNotFoundException, TasteException, IOException, OptionException {
        
        // create data source (model) - from the csv file            
        File ratingsFile = new File("datasets/dummy-bool.csv");                        
        DataModel model = new FileDataModel(ratingsFile);
        
        // create a simple recommender on our data
        CachingRecommender cachingRecommender = new CachingRecommender(new SlopeOneRecommender(model));

        // for all users
        for (LongPrimitiveIterator it = model.getUserIDs(); it.hasNext();){
            long userId = it.nextLong();
            
            // get the recommendations for the user
            List<RecommendedItem> recommendations = cachingRecommender.recommend(userId, 10);
            
            // if empty write something
            if (recommendations.size() == 0){
                System.out.print("User ");
                System.out.print(userId);
                System.out.println(": no recommendations");
            }
                            
            // print the list of recommendations for each 
            for (RecommendedItem recommendedItem : recommendations) {
                System.out.print("User ");
                System.out.print(userId);
                System.out.print(": ");
                System.out.println(recommendedItem);
            }
        }        
    }
}
```
Some notes to that:
  * If Java isn't your tongue language, be aware of the package declaration on the first line. If you omit that the Maven runner will never find your class.
  * In the main function we first create a data model from our csv file, then we instantiate a simple Slope One recommender filled with the data. Then we iterate over all users in the dataset and we print recommendations for them.
  * Sorry for my poor java.

To run the recommender on our dummy data, do:
```
mvn compile
```
This should end up by BUILD SUCCESSFUL. Then run the main function:
```
mvn exec:java -Dexec.mainClass="com.unresyst.UnresystBoolRecommend" 
```

In the middle of the Maven spam you should be able to see:
```
User 1: RecommendedItem[item:5, value:1.0]
User 2: RecommendedItem[item:5, value:1.0]
User 2: RecommendedItem[item:3, value:1.0]
User 3: no recommendations
User 4: no recommendations
User 5: RecommendedItem[item:5, value:1.0]
User 5: RecommendedItem[item:3, value:1.0]
```
These are recommendations for our users. Our recommender recommends the item `5` to the user `1`, with certainty 1.0 (this is a constant value for boolean recommenders), items `5` and `3` to user 2 and so on.

To reduce the Maven spam you can pass the `-q` option, to debug pass the `-e` option.

## Conclusion ##
That's it, now you've got your first Mahout recommender. You can now experiment with various data and various recommenders as described in other Mahout recommender tutorials. Some of the good ones:
  * A good starting guide, from which the example is partly overtaken: http://philippeadjiman.com/blog/2009/11/11/flexible-collaborative-filtering-in-java-with-mahout-taste/
  * The definitive IBM guide: http://www.ibm.com/developerworks/java/library/j-mahout/

Thanks for reading, any suggestions, corrections and comments are appreciated.

Sources and further reading
  * https://cwiki.apache.org/confluence/display/MAHOUT/Mahout+Wiki
  * https://cwiki.apache.org/confluence/display/MAHOUT/BuildingMahout
  * http://maven.apache.org/plugins/maven-surefire-plugin/howto.html
  * http://www.jarvana.com/jarvana/view/org/apache/mahout/mahout-core/0.4/mahout-core-0.4-javadoc.jar!/index-all.html
  * http://shuyo.wordpress.com/2011/02/14/mahout-development-environment-with-maven-and-eclipse-2/