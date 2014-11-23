/* ClusterApp.scala */
package ch.ethz.bigdata.cluster

import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD
import org.apache.spark.mllib.linalg.{ Vector, Vectors }
import org.apache.spark.mllib.feature.Normalizer
import com.typesafe.config._
import org.apache.spark.mllib.clustering.KMeans

object ClusterApp {
  def main(args: Array[String]) {
    /**
     * Parse parameters
     */
    val options: Map[String, String] = args.map { arg =>
      arg.dropWhile(_ == '-').split('=') match {
        case Array(opt, v) => (opt -> v)
        case Array(opt)    => (opt -> "true")
        case _             => throw new IllegalArgumentException("Invalid argument: " + arg)
      }
    }.toMap
    
    println(options)

    /**
     * Configure parameters
     */
    // AWS parameters
    val staticConfig = ConfigFactory.load()
    val awsAccessKey: String = staticConfig.getString("aws-config.AWS_ACCESS_KEY_ID")
    val awsSecretKey: String = staticConfig.getString("aws-config.AWS_SECRET_ACCESS_KEY")
    // Data related parameters
    val bucketName: String = "dj-byg-data"
    val dataPath: String = options.getOrElse("datapath", "output-2/part-00000")
    val clusterAssignmentOutputPath: String = "bygcluster-output/cluster-assignment-out-%d".format(System.currentTimeMillis())
    val clusterCentersOutputPath: String = "bygcluster-output/cluster-center-out-%d".format(System.currentTimeMillis())
    // Data Partitioning related parameters
    val enableCustomPartitioning: Boolean = options.getOrElse("part", "false").toBoolean
    val minParts: Int = options.getOrElse("minparts", "8").toInt
    // Clustering related parameters
    val numClusters: Int = options.getOrElse("k", "10").toInt
    val numIterations: Int = options.getOrElse("iters", "2").toInt
    
    println("---------------- Running with the following configuration ----------------")
    println("bucketName = " + bucketName)
    println("dataPath = " + dataPath)
    
    println("enableCustomPartitioning = " + enableCustomPartitioning)
    println("minParts = " + minParts)
    
    println("numClusters = " + numClusters)
    println("numIterations = " + numIterations)
    println("--------------------------------------------------------------------------")

    /**
     * Setup Spark
     */
    val conf = new SparkConf().setAppName("DJ Byg Cluster")
    val sc = new SparkContext(conf)
    val hadoopConf = sc.hadoopConfiguration
    hadoopConf.set("fs.s3n.impl", "org.apache.hadoop.fs.s3native.NativeS3FileSystem")
    hadoopConf.set("fs.s3n.awsAccessKeyId", awsAccessKey)
    hadoopConf.set("fs.s3n.awsSecretAccessKey", awsSecretKey)

    /**
     * Read file from S3
     * Then, convert into an intermediate RDD ready for clustering
     */
    val input_file = "s3n://%s/%s".format(bucketName, dataPath)
    val rawdata: RDD[String] =
      if (enableCustomPartitioning)
        sc.textFile(input_file, minParts)
      else
        sc.textFile(input_file)
    val normalizer = new Normalizer() // To Normalize the TF-IDF scores
    val alldata: RDD[(String, Vector)] = rawdata // Create SongID -> TF-IDF vector
      .map(line => (line.split(" ")(0), line.split(" ")(1)))
      .map {
        case (songID, xline) =>
          (songID, xline.split(",").map(_.toDouble))
      }
      .map {
        case (songID, arr) =>
          (songID, normalizer.transform(Vectors.dense(arr)))
      }

    // Extract only the vectors
    val traindata: RDD[Vector] = alldata.map(_._2).cache()

    /**
     * Perform k-means|| clustering
     * https://spark.apache.org/docs/latest/mllib-clustering.html
     */
    val clusters = KMeans.train(traindata, numClusters, numIterations)

    /**
     * Evaluate clustering
     */
    val WSSSE = clusters.computeCost(traindata)
    println("Within Set Sum of Squared Errors = " + WSSSE)

    /**
     * Extract necessary data for representing output
     */
    // Cluster assignment
    val clusterAssignment: RDD[(String, Int)] = alldata.map {
      case (songID, vec) =>
        (songID, clusters.predict(vec))
    }
    // Write this to S3
    clusterAssignment.saveAsTextFile("s3n://%s/%s".format(bucketName, clusterAssignmentOutputPath))

    // Cluster Centers
    val clusterCenters = clusters.clusterCenters
    val clusterCentersRDD = sc.parallelize(clusterCenters)
    // Write Cluster Centers to RDD
    clusterCentersRDD.saveAsTextFile("s3n://%s/%s".format(bucketName, clusterCentersOutputPath))

    /**
     * Push to DynamoDB
     */

  }
}