package com.aster.zhbj;

import com.github.unidbg.AndroidEmulator;
import com.github.unidbg.linux.android.AndroidEmulatorBuilder;
import com.github.unidbg.linux.android.AndroidResolver;
import com.github.unidbg.linux.android.dvm.DalvikModule;
import com.github.unidbg.linux.android.dvm.DvmClass;
import com.github.unidbg.linux.android.dvm.StringObject;
import com.github.unidbg.linux.android.dvm.VM;
import com.github.unidbg.linux.android.dvm.jni.ProxyClassFactory;
import com.github.unidbg.memory.Memory;

import java.io.*;

public class Signutil {
    private final AndroidEmulator emulator;

    private final DvmClass cSignUtil;
    private final VM vm;
    // so文件路径（自动处理了中文路径）
    public final static String soPath = System.getProperty("user.dir") + File.separator + "libnativecore.so";

    public Signutil() {
        emulator = AndroidEmulatorBuilder.for64Bit()
                .setProcessName("com.aster.zhbj")
                .build();
        Memory memory = emulator.getMemory();
        memory.setLibraryResolver(new AndroidResolver(23));
        vm = emulator.createDalvikVM();
        vm.setDvmClassFactory(new ProxyClassFactory());
        vm.setVerbose(false);
        DalvikModule dm = vm.loadLibrary(new File(soPath), false);
        cSignUtil = vm.resolveClass("com/aster/nativecore/NativeLib");
        dm.callJNI_OnLoad(emulator);

        // emulator.traceCode();
    }

    public void destroy() throws IOException {
        emulator.close();
    }

    public String getShortSign(String p1) {
        String methodSign = "getShortSign(Ljava/lang/String)Ljava/lang/String;";
        StringObject obj = cSignUtil.callStaticJniMethodObject(emulator, methodSign, p1);
        return obj.getValue();
    }

    public String getSign(String p1) {
        String methodSign = "getSign(Ljava/lang/String)Ljava/lang/String;";
        StringObject obj = cSignUtil.callStaticJniMethodObject(emulator, methodSign, p1);
        return obj.getValue();
    }

    public static void inputStreamToFile(InputStream inputStream, String targetFilePath) {
        File file = new File(targetFilePath);
        try {
            OutputStream os = new FileOutputStream(file);
            int bytesRead = 0;
            byte[] buffer = new byte[8192];
            while ((bytesRead = inputStream.read(buffer, 0, 8192)) != -1) {
                os.write(buffer, 0, bytesRead);
            }
            os.close();
            inputStream.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        File so = new File(Signutil.soPath);
        if (!so.exists()) {
            InputStream inputStream = Signutil.class.getClassLoader().getResourceAsStream("libnativecore.so");
            // 获取当前jar包所在目录,释放so文件
            inputStreamToFile(inputStream, so.getAbsolutePath());
            System.out.println("释放so文件成功:"+so.getAbsolutePath());
        }

        Signutil signutil = new Signutil();
        String shortSign = signutil.getShortSign("df8xxxxxx64ddf|1696520079967|0|0|com.aster.zhbj");
        System.out.println("sign=" + shortSign);
        String sign = signutil.getSign("1673426429892|d9b758xxxxxfb88d|1669337826366");
        System.out.println("sign1=" + sign);
        try {
            signutil.destroy();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
